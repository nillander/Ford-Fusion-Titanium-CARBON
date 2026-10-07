// meshoptimizer 1.3.0, MIT; download documented in tools/README.md.
import { MeshoptSimplifier } from '../tools/vendor/meshoptimizer/package/meshopt_simplifier.js';
import { readFile, writeFile } from 'node:fs/promises';
const root = new URL('../', import.meta.url);
const dir = new URL('work/simplification2018/', root);
await MeshoptSimplifier.ready;
async function array(name, Type) {
  const bytes = await readFile(new URL(name, dir));
  return new Type(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
}
const report = [];
for (const job of JSON.parse(await readFile(new URL('jobs.json', dir), 'utf8'))) {
  const positions = await array(job.name + '.positions.bin', Float32Array);
  const attributes = await array(job.name + '.attributes.bin', Float32Array);
  const indices = await array(job.name + '.indices.bin', Uint32Array);
  let offset = 0, total = 0;
  const groups = [];
  for (let i = 0; i < job.groups.length; i++) {
    const count = job.groups[i];
    const target = Math.max(3, Math.floor(count * 65400 / job.indices / 3) * 3);
    const [result, error] = count === 0 ? [new Uint32Array(), 0] :
      MeshoptSimplifier.simplifyWithAttributes(indices.subarray(offset, offset + count), positions, 3,
        attributes, 5, [0.1, 0.1, 0.1, 1, 1], null, target, 0.01, ['Sparse', 'Permissive']);
    await writeFile(new URL(`${job.name}.${i}.bin`, dir), new Uint8Array(result.buffer));
    groups.push({original_indices: count, indices: result.length, relative_weighted_error: error});
    offset += count; total += result.length;
  }
  const record = {name: job.name, original_indices: indices.length, indices: total,
    within_carbon_limit: total <= 65535, groups};
  report.push(record);
  console.log(job.name, indices.length, '->', total, record.within_carbon_limit ? 'PASS' : 'OVER LIMIT');
}
await writeFile(new URL('docs/carbon2018-simplification.json', root), JSON.stringify(report, null, 2) + '\n');
if (report.some(r => !r.within_carbon_limit)) process.exitCode = 1;
