/** Versioned local persistence. Never replace the last valid backup with corrupt data. */
export function loadSaved(storage, key, validate, create, legacyKeys=[]) {
  let accessible=true;
  for (const candidate of [key, key+'.backup', ...legacyKeys]) {
    let raw;
    try { raw=storage.getItem(candidate); }
    catch { accessible=false; continue; }
    if (!raw) continue;
    try { return {value:validate(JSON.parse(raw)),ok:accessible,recovered:candidate!==key,source:candidate}; }
    catch { /* A broken main save must not prevent recovery from a valid backup. */ }
  }
  return {value:create(),ok:accessible,recovered:false,source:null};
}
export function saveSafely(storage, key, value, validate) {
  try {
    const checked=validate(value), raw=JSON.stringify(checked);
    const old=storage.getItem(key);
    if (old && old!==raw) {
      try { validate(JSON.parse(old)); storage.setItem(key+'.backup',old); }
      catch { /* Keep the existing backup when the previous primary is not valid. */ }
    }
    storage.setItem(key,raw);
    // The first successful save also has a recovery copy.
    if (!storage.getItem(key+'.backup')) {
      try { storage.setItem(key+'.backup',raw); } catch { /* Primary still saved. */ }
    }
    return true;
  } catch { return false; }
}
