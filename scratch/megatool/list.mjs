import { File } from 'megajs'
const url = 'https://mega.nz/folder/05pBGLAL#XPHcsgK2tBxT3RLMbZPaFw'
const folder = File.fromURL(url)
await folder.loadAttributes()
const walk = (f, pre='') => { for (const c of (f.children||[])) { console.log(pre + c.name, c.directory ? '(dir)' : c.size); if (c.directory) walk(c, pre + '  ') } }
console.log('ROOT', folder.name); walk(folder)
