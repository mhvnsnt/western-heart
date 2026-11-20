import { rename, leaks } from './canon.mjs';
import assert from 'node:assert';
const m = [{ original: 'Heat Action', canon: 'Ember Rite', source: 'yakuza-kiwami', kind: 'system' }];
assert.equal(rename({ n: 'Heat Action: Wall' }, m).n, 'Ember Rite: Wall');
assert.deepEqual(leaks('a Fire Pro move', ['fire pro']), ['fire pro']);
assert.deepEqual(leaks('Ember Rite', ['heat action']), []);
console.log('canon tests ok');
