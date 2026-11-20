// cue4-export — headless CUE4Parse exporter for Tekken 8 (UE5 IoStore). STATUS: scaffold, not yet run
// against real T8 Paks (none on the box as of 2026-10-23). First run: fix API drift, pin versions, log here.
// Exports: AnimSequence -> .psa, SkeletalMesh -> .psk/.gltf, Texture2D -> .png, DataTable/other -> .json.
using System; using System.IO; using System.Linq; using System.Collections.Generic;
using CUE4Parse.FileProvider; using CUE4Parse.UE4.Versions; using CUE4Parse.Encryption.Aes;
using CUE4Parse.UE4.Objects.Core.Misc; using CUE4Parse.UE4.Assets.Exports.Animation;
using CUE4Parse.UE4.Assets.Exports.SkeletalMesh; using CUE4Parse.UE4.Assets.Exports.Texture;
using CUE4Parse_Conversion; using CUE4Parse_Conversion.Textures; using Newtonsoft.Json;

class P {
  static string Arg(string[] a, string k) { int i = Array.IndexOf(a, k); return i >= 0 && i + 1 < a.Length ? a[i + 1] : null; }
  static void Main(string[] a) {
    string paks = Arg(a, "--paks"), outDir = Arg(a, "--out");
    var game = Enum.Parse<EGame>(Arg(a, "--game") ?? "GAME_UE5_LATEST");
    int fi = Array.IndexOf(a, "--filters"); var filters = fi >= 0 ? a.Skip(fi + 1).ToList() : new List<string>();
    var key = Environment.GetEnvironmentVariable("T8_AES_KEY") ?? throw new Exception("T8_AES_KEY unset");
    var prov = new DefaultFileProvider(paks, SearchOption.TopDirectoryOnly, true, new VersionContainer(game));
    prov.Initialize();
    prov.SubmitKey(new FGuid(), new FAesKey(key));
    prov.LoadLocalization();
    Directory.CreateDirectory(outDir);
    using var man = new StreamWriter(Path.Combine(outDir, "MANIFEST.tsv"));
    man.WriteLine("path\tsize\tkind\texported");
    var opts = new ExporterOptions();
    foreach (var (path, file) in prov.Files) {
      if (!path.EndsWith(".uasset")) continue;
      if (filters.Count > 0 && !filters.Any(f => path.Contains(f, StringComparison.OrdinalIgnoreCase))) continue;
      string kind = "?", exported = "";
      try {
        foreach (var ex in prov.LoadAllObjects(path)) {
          kind = ex.ExportType;
          var dst = new DirectoryInfo(outDir);
          if (ex is UAnimSequence || ex is USkeletalMesh || ex is USkeleton) {
            var exp = new Exporter(ex, opts);
            exp.TryWriteToDir(dst, out _, out var saved); exported = saved;
          } else if (ex is UTexture2D tex) {
            var bmp = tex.Decode(); if (bmp != null) {
              var o = Path.Combine(outDir, path.Replace(".uasset", ".png")); Directory.CreateDirectory(Path.GetDirectoryName(o));
              using var fs = File.OpenWrite(o); bmp.Encode(SkiaSharp.SKEncodedImageFormat.Png, 100).SaveTo(fs); exported = o; }
          } else {
            var o = Path.Combine(outDir, path.Replace(".uasset", ".json")); Directory.CreateDirectory(Path.GetDirectoryName(o));
            File.WriteAllText(o, JsonConvert.SerializeObject(ex, Formatting.Indented)); exported = o;
          }
        }
      } catch (Exception e) { exported = "ERR " + e.Message; }
      man.WriteLine($"{path}\t{file.Size}\t{kind}\t{exported}");
    }
  }
}
