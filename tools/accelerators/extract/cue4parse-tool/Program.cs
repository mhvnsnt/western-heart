// CUE4ParseTool — scripted UE asset reads via CUE4Parse (built on demand by
// extract.sh; never vendored). v1 commands:
//   list <pakdir>       --ue <4.27|5.x> [--aes KEY] [--filter GLOB]
//   export-tex <pakdir> --ue <4.27|5.x> --out DIR [--aes KEY] [--filter GLOB]
//
// Mesh/animation geometry export is intentionally NOT here — UModel's CLI
// (extract.sh umodel-export) is the batch workhorse for PSK/PSA; FModel on
// Windows covers the rest. This tool does what CUE4Parse is best at in a
// pipeline: scripted listing and texture extraction.
using System.Text.RegularExpressions;
using CUE4Parse.Encryption.Aes;
using CUE4Parse.FileProvider;
using CUE4Parse.UE4.Assets;
using CUE4Parse.UE4.Assets.Exports.Texture;
using CUE4Parse.UE4.Versions;
using CUE4Parse.Utils;
using SkiaSharp;

var argList = args.ToList();
if (argList.Count == 0) { Usage(); return 1; }
var cmd = argList[0];
var rest = argList.Skip(1).ToList();

string GetOpt(string name, string? def = null)
{
    var i = rest.IndexOf(name);
    if (i < 0 || i + 1 >= rest.Count) return def!;
    return rest[i + 1];
}

try
{
    return cmd switch
    {
        "list" => CmdList(rest, GetOpt),
        "export-tex" => CmdExportTex(rest, GetOpt),
        _ => { Usage(); return 1; }
    };
}
catch (Exception e)
{
    Console.Error.WriteLine($"ERROR: {e.Message}");
    return 2;
}

void Usage()
{
    Console.Error.WriteLine("""
        usage: CUE4ParseTool <list|export-tex> <pakdir> --ue <4.27|5.x> [--aes KEY] [--filter GLOB] [--out DIR]
          list        print virtual paths + sizes of files in the mounted paks
          export-tex  export UTexture2D assets to PNG
        """);
}

EGame ParseUe(string v)
{
    var name = "GAME_UE" + v.Replace(".", "_");
    if (Enum.TryParse<EGame>(name, out var g)) return g;
    throw new ArgumentException($"unknown --ue version '{v}' (tried {name})");
}

DefaultFileProvider Mount(string pakdir, string ue, string? aes)
{
    var provider = new DefaultFileProvider(pakdir, SearchOption.TopDirectoryOnly, true,
        new VersionContainer(ParseUe(ue)));
    provider.Initialize();
    if (!string.IsNullOrEmpty(aes))
    {
        var key = new FAesKey(aes);
        foreach (var reader in provider.UnloadedVfs)
            provider.SubmitKey(reader.EncryptionKeyGuid, key);
    }
    return provider;
}

Regex? ToRegex(string? glob)
{
    if (string.IsNullOrEmpty(glob)) return null;
    return new Regex("^" + Regex.Escape(glob).Replace(@"\*", ".*").Replace(@"\?", ".") + "$",
        RegexOptions.IgnoreCase | RegexOptions.Compiled);
}

int CmdList(List<string> rest, Func<string, string?, string?> getOpt)
{
    var pakdir = rest.FirstOrDefault(x => !x.StartsWith("--")) ?? throw new ArgumentException("missing <pakdir>");
    var ue = getOpt("--ue", null) ?? throw new ArgumentException("--ue required");
    var filter = ToRegex(getOpt("--filter", null));
    using var provider = Mount(pakdir, ue, getOpt("--aes", null));
    long total = 0; int n = 0;
    foreach (var kv in provider.Files.OrderBy(kv => kv.Key))
    {
        if (filter != null && !filter.IsMatch(kv.Key)) continue;
        Console.WriteLine($"{kv.Value.Size,12}  {kv.Key}");
        total += kv.Value.Size; n++;
    }
    Console.Error.WriteLine($"==> {n} files, {total / 1024 / 1024} MiB (virtual, inside paks)");
    return 0;
}

int CmdExportTex(List<string> rest, Func<string, string?, string?> getOpt)
{
    var pakdir = rest.FirstOrDefault(x => !x.StartsWith("--")) ?? throw new ArgumentException("missing <pakdir>");
    var ue = getOpt("--ue", null) ?? throw new ArgumentException("--ue required");
    var outDir = getOpt("--out", null) ?? throw new ArgumentException("--out DIR required");
    var filter = ToRegex(getOpt("--filter", null));
    Directory.CreateDirectory(outDir);
    using var provider = Mount(pakdir, ue, getOpt("--aes", null));
    int ok = 0, fail = 0, skipped = 0;
    foreach (var path in provider.Files.Keys.OrderBy(k => k))
    {
        if (!path.EndsWith(".uasset", StringComparison.OrdinalIgnoreCase)) continue;
        if (filter != null && !filter.IsMatch(path)) continue;
        UObject? obj;
        try { obj = provider.LoadObject(path.SubstringBeforeLast('.')); }
        catch { fail++; continue; }
        if (obj is not UTexture2D tex) { skipped++; continue; }
        try
        {
            using var bmp = tex.Decode(ETexturePlatform.DesktopMobile);
            if (bmp == null) { fail++; continue; }
            var safe = path.Replace('/', '_').Replace('\\', '_');
            var dest = Path.Combine(outDir, safe.SubstringBeforeLast('.') + ".png");
            using var fs = File.OpenWrite(dest);
            bmp.Encode(SKEncodedImageFormat.Png, 100).SaveTo(fs);
            ok++;
        }
        catch (Exception e) { Console.Error.WriteLine($"  skip {path}: {e.Message}"); fail++; }
    }
    Console.Error.WriteLine($"==> textures exported: {ok} ok, {fail} failed, {skipped} non-texture uassets skipped -> {outDir}");
    return fail > 0 && ok == 0 ? 2 : 0;
}
