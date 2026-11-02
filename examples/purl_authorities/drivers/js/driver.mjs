// driver.mjs - Run packageurl-js on the corpus and print one JSON array.
//
// WHAT: Reads corpus.csv (row, set_id, family, input). For each input it calls
//       PackageURL.fromString and then toString, and records the normalized string
//       or the error text.
// WHY:  An independently developed implementation of the Package URL specification,
//       used as a second authority for the same operation as packageurl-python.
// OBS:  This file adds no normalization rules of its own. The corpus has no quoted
//       commas or newlines, so a line split is enough to read it.

import { readFileSync } from 'node:fs'
import { PackageURL } from 'packageurl-js'

const lines = readFileSync(process.argv[2], 'utf8').split('\n').filter((line, index) => index > 0 && line !== '')
const results = lines.map((line) => {
  const [row, , , ...rest] = line.split(',')
  const input = rest.join(',')
  try {
    return { row, ok: true, output: PackageURL.fromString(input).toString(), error: '' }
  } catch (error) {
    return { row, ok: false, output: '', error: String(error.message) }
  }
})
process.stdout.write(JSON.stringify(results, null, 2) + '\n')
