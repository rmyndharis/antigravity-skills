const fs = require('fs-extra');
const path = require('path');

async function statIfPresent(filePath) {
  try {
    return await fs.lstat(filePath);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

async function realPath(filePath) {
  try {
    return await fs.realpath(filePath);
  } catch (err) {
    if (err.code !== 'ENOENT' || await statIfPresent(filePath)) throw err;
    const parent = path.dirname(filePath);
    if (parent === filePath) throw err;
    return path.join(await realPath(parent), path.basename(filePath));
  }
}

function contains(parent, child) {
  const relative = path.relative(parent, child);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
}

async function validateSkillDirectory(directory) {
  const directoryStat = await statIfPresent(directory);
  const skillStat = await statIfPresent(path.join(directory, 'SKILL.md'));
  if (!directoryStat || !directoryStat.isDirectory() || !skillStat || !skillStat.isFile() || skillStat.size === 0) {
    throw new Error(`Skill directory must contain a nonempty regular SKILL.md: ${directory}`);
  }
}

async function validatePaths(sourcePath, destPath) {
  await validateSkillDirectory(sourcePath);
  const destStat = await statIfPresent(destPath);
  if (destStat && !destStat.isDirectory()) {
    throw new Error(`Installation destination must be a real directory, not a file or symlink: ${destPath}`);
  }
  const source = await realPath(sourcePath);
  const destination = await realPath(destPath);
  if (contains(source, destination) || contains(destination, source)) {
    throw new Error('Skill source and installation destination must not overlap.');
  }
  return { source, destination, exists: Boolean(destStat) };
}

async function installSkill(sourcePath, destPath, overwrite = false) {
  const paths = await validatePaths(sourcePath, destPath);
  const parent = path.dirname(paths.destination);
  await fs.ensureDir(parent);
  const lockPath = path.join(parent, `.${path.basename(destPath)}.install-lock`);
  try {
    await fs.mkdir(lockPath);
  } catch (err) {
    if (err.code === 'EEXIST') {
      throw new Error(`Another installation may be in progress. If none is running, remove the stale lock: ${lockPath}`);
    }
    throw err;
  }

  let workDir;
  let retainBackup = false;
  try {
    const current = await validatePaths(sourcePath, destPath);
    if (current.source !== paths.source || current.destination !== paths.destination) {
      throw new Error('Skill source or installation destination changed while preparing the installation.');
    }
    if (current.exists && !overwrite) return false;

    workDir = await fs.mkdtemp(path.join(parent, `.${path.basename(destPath)}.install-`));
    const stagedPath = path.join(workDir, 'staged');
    const backupPath = path.join(workDir, 'backup');
    fs.copySync(paths.source, stagedPath, {
      overwrite: false,
      errorOnExist: true,
      filter: filePath => {
        if (fs.lstatSync(filePath).isSymbolicLink()) {
          throw new Error(`Skill source must not contain symlinks: ${filePath}`);
        }
        return true;
      },
    });

    const ready = await validatePaths(sourcePath, destPath);
    if (ready.source !== paths.source || ready.destination !== paths.destination) {
      throw new Error('Skill source or installation destination changed while preparing the installation.');
    }
    if (ready.exists && !overwrite) return false;
    await validateSkillDirectory(stagedPath);
    if (ready.exists) await fs.rename(paths.destination, backupPath);
    try {
      await fs.rename(stagedPath, paths.destination);
    } catch (err) {
      if (ready.exists) {
        try {
          await fs.rename(backupPath, paths.destination);
        } catch (restoreError) {
          retainBackup = true;
          throw new Error(`Installation failed (${err.message}); restoration failed (${restoreError.message}). Previous installation retained at: ${backupPath}`);
        }
      }
      throw err;
    }
    return true;
  } finally {
    if (workDir && !retainBackup) {
      try {
        await fs.remove(workDir);
      } catch (err) {
        console.warn(`Warning: Could not remove installation temporary files at ${workDir}: ${err.message}`);
      }
    }
    try {
      await fs.rmdir(lockPath);
    } catch (err) {
      console.warn(`Warning: Could not remove installation lock at ${lockPath}: ${err.message}`);
    }
  }
}

module.exports = { installSkill };
