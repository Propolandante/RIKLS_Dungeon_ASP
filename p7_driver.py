import p7_visualize
import sys
import json
import collections
import subprocess

"""
gringo level-core.lp level-style.lp level-sim.lp level-shortcuts.lp | reify | clingo - meta.lp metaD.lp metaO.lp metaS.lp --parallel-mode=4 --outf=2
"""

def main():
	solve()

def solve():
    # gringo level-core.lp level-style.lp level-sim.lp level-shortcuts.lp | reify | clingo - meta.lp metaD.lp metaO.lp metaS.lp --parallel-mode=4 --outf=2 > example_noshortcut.json
    # becomes

    gringo = subprocess.Popen(["gringo", "level-core.lp", "level-style.lp", "level-sim.lp", "level-shortcuts.lp"],
    	stdout = subprocess.PIPE,
    	stderr = subprocess.PIPE)
    reify = subprocess.Popen(["reify"],
    	stdin = gringo.stdout,
    	stdout = subprocess.PIPE,
    	stderr = subprocess.PIPE)
    clingo = subprocess.Popen(["clingo", "-", "meta.lp", "metaD.lp", "metaO.lp", "metaS.lp", "--parallel-mode=4", "--outf=2"],
    	stdin = reify.stdout,
    	stdout = subprocess.PIPE,
    	stderr = subprocess.PIPE)
    gringo.stdout.close()
    reify.stdout.close()

    output, error = clingo.communicate()

    print output

    dungeon = parse_json_result(output)

    print render_ascii_dungeon(dungeon)

def parse_json_result(out):
    """Parse the provided JSON text and extract a dict
    representing the predicates described in the first solver result."""

    result = json.loads(out)
    
    assert len(result['Call']) > 0
    assert len(result['Call'][0]['Witnesses']) > 0
    
    witness = result['Call'][0]['Witnesses'][0]['Value']
    
    class identitydefaultdict(collections.defaultdict):
        def __missing__(self, key):
            return key
    
    preds = collections.defaultdict(set)
    env = identitydefaultdict()
    
    for atom in witness:
        if '(' in atom:
            left = atom.index('(')
            functor = atom[:left]
            arg_string = atom[left:]
            try:
                preds[functor].add( eval(arg_string, env) )
            except TypeError:
                pass # at least we tried...
            
        else:
            preds[atom] = True
    
    return dict(preds)


def render_ascii_dungeon(design):
    """Given a dict of predicates, return an ASCII-art depiction of the a dungeon."""
    
    sprite = dict(design['sprite'])
    param = dict(design['param'])
    width = param['width']
    glyph = dict(space='.', wall='W', altar='a', gem='g', trap='_')
    block = ''.join([''.join([glyph[sprite.get((r,c),'space')]+' ' for c in range(width)])+'\n' for r in range(width)])
    return block

if __name__ == "__main__":
    main()