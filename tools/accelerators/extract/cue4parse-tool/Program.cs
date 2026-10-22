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
using CUE4Parse.UE4.Assets.Exports;
using CUE4Parse.UE4.Assets.Exports.Texture;
using CUE4Parse.UE4.Versions;
using CUE4Parse.Utils;
using CUE4Parse_Conversion.Textures;

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

int exitCode;
try
{
    switch (cmd)
    {
        case "list": exitCode = CmdList(rest, GetOpt); break;
        case "export-tex": exitCode = CmdExportTex(rest, GetOpt); break;
        default: Usage(); exitCode = 1; break;
    }
}
catch (Exception e)
{
    Console.Error.WriteLine($"ERROR: {e.Message}");
    exitCode = 2;
}
return exitCode;

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
        try { obj = provider.LoadPackageObject<UObject>(path.SubstringBeforeLast('.')); }
        catch { fail++; continue; }
        if (obj is not UTexture2D tex) { skipped++; continue; }
        try
        {
            var ct = tex.Decode(ETexturePlatform.DesktopMobile);
            if (ct == null) { fail++; continue; }
            var rgba = ToRgba8(ct);
            if (rgba == null) { Console.Error.WriteLine($"  skip {path}: pixel format {ct.PixelFormat}"); fail++; continue; }
            var safe = path.Replace('/', '_').Replace('\\', '_');
            var dest = Path.Combine(outDir, safe.SubstringBeforeLast('.') + ".png");
            WritePng(dest, ct.Width, ct.Height, rgba);
            ok++;
        }
        catch (Exception e) { Console.Error.WriteLine($"  skip {path}: {e.Message}"); fail++; }
    }
    Console.Error.WriteLine($"==> textures exported: {ok} ok, {fail} failed, {skipped} non-texture uassets skipped -> {outDir}");
    return fail > 0 && ok == 0 ? 2 : 0;
}

// Decode output is RGBA8 or BGRA8 (see TextureDecoder.DecodeTexture);
// normalize to RGBA8, else null (logged + skipped by the caller).
byte[]? ToRgba8(CTexture ct)
{
    if (ct.PixelFormat == EPixelFormat.PF_R8G8B8A8) return ct.Data;
    if (ct.PixelFormat == EPixelFormat.PF_B8G8R8A8)
    {
        var d = (byte[])ct.Data.Clone();
        for (int i = 0; i + 3 < d.Length; i += 4) (d[i], d[i + 2]) = (d[i + 2], d[i]);
        return d;
    }
    return null;
}

// Minimal PNG writer: 8-bit RGBA, no interlace. zlib stream is built by hand
// (2-byte header + raw deflate + Adler-32) so there's no extra dependency.
void WritePng(string dest, int w, int h, byte[] rgba)
{
    using var ms = new MemoryStream();
    ms.Write(new byte[] { 137, 80, 78, 71, 13, 10, 26, 10 }); // signature
    void Chunk(string type, byte[] data)
    {
        var t = System.Text.Encoding.ASCII.GetBytes(type);
        ms.Write(BitConverter.GetBytes((uint)data.Length).Reverse().ToArray());
        ms.Write(t); ms.Write(data);
        uint crc = Crc32(t.Concat(data).ToArray());
        ms.Write(BitConverter.GetBytes(crc).Reverse().ToArray());
    }
    var ihdr = new byte[13];
    Buffer.BlockCopy(BitConverter.GetBytes((uint)w).Reverse().ToArray(), 0, ihdr, 0, 4);
    Buffer.BlockCopy(BitConverter.GetBytes((uint)h).Reverse().ToArray(), 0, ihdr, 4, 4);
    ihdr[8] = 8; ihdr[9] = 6; // 8-bit, truecolor+alpha
    Chunk("IHDR", ihdr);
    // scanlines with filter byte 0, deflated
    var raw = new byte[(w * 4 + 1) * h];
    for (int y = 0; y < h; y++) { raw[y * (w * 4 + 1)] = 0; Buffer.BlockCopy(rgba, y * w * 4, raw, y * (w * 4 + 1) + 1, w * 4); }
    using var comp = new MemoryStream();
    using (var ds = new System.IO.Compression.DeflateStream(comp, System.IO.Compression.CompressionLevel.Optimal, true))
        ds.Write(raw, 0, raw.Length);
    var deflated = comp.ToArray();
    var zlib = new byte[2 + deflated.Length + 4];
    zlib[0] = 0x78; zlib[1] = 0x9C; // zlib header
    Buffer.BlockCopy(deflated, 0, zlib, 2, deflated.Length);
    Buffer.BlockCopy(BitConverter.GetBytes(Adler32(raw)).Reverse().ToArray(), 0, zlib, 2 + deflated.Length, 4);
    Chunk("IDAT", zlib);
    Chunk("IEND", Array.Empty<byte>());
    File.WriteAllBytes(dest, ms.ToArray());
}

uint Crc32(byte[] data)
{
    uint c = 0xFFFFFFFF;
    for (int n = 0; n < data.Length; n++)
    {
        c ^= data[n];
        for (int k = 0; k < 8; k++) c = (c & 1) != 0 ? 0xEDB88320u ^ (c >> 1) : c >> 1;
    }
    return ~c;
}

uint Adler32(byte[] data)
{
    uint a = 1, b = 0;
    foreach (var x in data) { a = (a + x) % 65521; b = (b + a) % 65521; }
    return (b << 16) | a;
}
