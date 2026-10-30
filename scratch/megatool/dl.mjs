import { File } from 'megajs'
import fs from 'node:fs'
const folder = File.fromURL('https://mega.nz/folder/05pBGLAL#XPHcsgK2tBxT3RLMbZPaFw')
await folder.loadAttributes()
const f = folder.children.find(c => c.name === 'TekkenMannequin_no_ik.blend')
const buf = await f.downloadBuffer()
fs.writeFileSync(process.argv[2], buf)
console.log('saved', buf.length)
