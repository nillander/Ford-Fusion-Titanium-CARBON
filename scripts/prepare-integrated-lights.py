"""Combine Fusion lamp housing and lens OBJ for the main Carbon light parts."""
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    source=ROOT/'work/carbon2018-source-axes'
    dest=ROOT/'work/carbon2018-integrated-light-source'
    dest.mkdir(exist_ok=True)
    records=[]
    for family in ['HEADLIGHT','BRAKELIGHT']:
        for lod in 'ABCD':
            name=f'KIT00_RIGHT_{family}_{lod}'
            housing=(source/(name+'.obj')).read_text()
            lens=(source/(f'KIT00_RIGHT_{family}_GLASS_{lod}.obj')).read_text()
            offsets={tag:sum(line.startswith(tag+' ') for line in housing.splitlines()) for tag in ['v','vt','vn']}
            lines=[housing.rstrip()]
            triangles=0
            for line in lens.splitlines():
                if line.startswith(('g ','o ')):continue
                if line.startswith('f '):
                    face=[]
                    for item in line.split()[1:]:
                        indices=item.split('/')
                        assert len(indices)==3 and all(int(v)>0 for v in indices)
                        face.append('/'.join(str(int(v)+offsets[tag]) for v,tag in zip(indices,['v','vt','vn'])))
                    line='f '+' '.join(face)
                    triangles+=1
                lines.append(line)
            output='\n'.join(lines)+'\n'
            count=sum(line.startswith('f ') for line in output.splitlines())*3
            assert count<=65535
            (dest/(name+'.obj')).write_text(output,encoding='ascii')
            records.append({'part':'MUSTANGGT_'+name,'indices':count,'lens_triangles':triangles})
    shutil.copyfile(source/'matlist.txt',dest/'matlist.txt')
    (dest/'mpoints.txt').write_text('# Light parts have no mount markers.\n')
    (dest/'link.txt').write_text('# Explicit A-D lights.\n')
    (ROOT/'docs/carbon2018-integrated-lights-plan.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Prepared 8 main lights with integrated lenses; max indices',max(r['indices'] for r in records))

if __name__=='__main__':main()
