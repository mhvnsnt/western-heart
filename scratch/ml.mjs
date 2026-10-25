const R='/home/user/western-heart/game/js/';
const { registerMoveset } = await import(R+'movesets.js');
const { movelistRows, filterMovelist } = await import(R+'movelist-ui.js');
registerMoveset('test-fighter', { moves: {
  '1': { name: 'Jab', input: '1', damage: 7, startup: 0.117, move_class: 'strike' },
  '2,1': { name: 'String', input: '2,1', damage: 14, startup: 0.2, move_class: 'string' },
  '1+2': { name: 'Power', input: '1+2', damage: 25, startup: 0.35, move_class: 'special' },
}});
const rows = movelistRows('test-fighter');
console.log(rows.map(r=>[r.notation,r.key,r.moveClass,r.name, r.origin].join('|')).join('\n'));
