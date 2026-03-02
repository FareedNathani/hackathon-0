const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = 5000;

app.use(cors());
app.use(bodyParser.json());

// Configuration - Pointing to the AI Employee Vault relative to the server location
const VAULT_ROOT = path.resolve(__dirname, '../../AI_Employee_Vault');
const DIRS = {
  inbox: path.join(VAULT_ROOT, 'Inbox'),
  needsAction: path.join(VAULT_ROOT, 'Needs_Action'),
  needsApproval: path.join(VAULT_ROOT, 'Needs_Approval'),
  done: path.join(VAULT_ROOT, 'Done')
};

// Helper to list files
const getFiles = (dir) => {
  try {
    if (!fs.existsSync(dir)) return [];
    return fs.readdirSync(dir).filter(f => f.endsWith('.md'));
  } catch (e) {
    console.error(`Error reading ${dir}:`, e);
    return [];
  }
};

// Helper to read file content
const readFile = (filePath) => {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch (e) {
    return `Error reading file: ${e.message}`;
  }
};

// API: Get Dashboard Stats & Tasks
app.get('/api/dashboard', (req, res) => {
  const data = {
    inbox: getFiles(DIRS.inbox).map(f => ({ name: f, path: path.join(DIRS.inbox, f) })),
    needsAction: getFiles(DIRS.needsAction).map(f => ({ name: f, path: path.join(DIRS.needsAction, f) })),
    needsApproval: getFiles(DIRS.needsApproval).map(f => ({ name: f, path: path.join(DIRS.needsApproval, f) })),
    done: getFiles(DIRS.done).map(f => ({ name: f, path: path.join(DIRS.done, f) }))
  };
  res.json(data);
});

// API: Get File Content
app.get('/api/file', (req, res) => {
  const { filePath } = req.query;
  if (!filePath) return res.status(400).json({ error: 'Missing filePath' });
  
  // Security check: ensure path is within vault
  if (!path.resolve(filePath).startsWith(VAULT_ROOT)) {
    return res.status(403).json({ error: 'Access denied: Path outside vault.' });
  }

  const content = readFile(filePath);
  res.json({ content });
});

// API: Approve Task
app.post('/api/approve', (req, res) => {
  const { fileName } = req.body;
  if (!fileName) return res.status(400).json({ error: 'Missing fileName' });

  const filePath = path.join(DIRS.needsApproval, fileName);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'File not found' });

  try {
    let content = fs.readFileSync(filePath, 'utf-8');
    // Replace existing status or append
    if (content.includes('Status: PENDING')) {
      content = content.replace('Status: PENDING', 'Status: APPROVED');
    } else {
      content += '

Status: APPROVED';
    }
    fs.writeFileSync(filePath, content);
    res.json({ success: true, message: 'Task approved successfully.' });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Create Task
app.post('/api/create', (req, res) => {
  const { title, description, priority } = req.body;
  if (!title || !description) return res.status(400).json({ error: 'Missing fields' });

  const fileName = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`;
  const filePath = path.join(DIRS.inbox, fileName);

  const content = `# ${title}

${description}

Priority: ${priority || 'Medium'}`;

  try {
    fs.writeFileSync(filePath, content);
    res.json({ success: true, message: 'Task created in Inbox.' });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// API: Trigger Platinum Executor
app.post('/api/trigger', (req, res) => {
  const scriptPath = path.resolve(__dirname, '../../scripts/platinum_executor.py');
  exec(`python "${scriptPath}"`, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return res.status(500).json({ error: stderr || error.message });
    }
    res.json({ success: true, output: stdout });
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Connected to Vault at: ${VAULT_ROOT}`);
});
