# RunPod Setup Troubleshooting

Common issues and solutions from real workshop testing.

## SSH Connection Issues

### Adding SSH Key to RunPod
1. Get your SSH public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
2. Copy the ENTIRE line (including `ssh-ed25519` and the email/comment at the end)
3. In RunPod Settings → SSH Keys → Paste and Update

### First Connection - Fingerprint Verification
When connecting for the first time, you'll see:
```
The authenticity of host 'ssh.runpod.io' can't be established.
RSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no)?
```
**Solution**: Type `yes` and press Enter. This is normal security verification.

### Two SSH Options from RunPod
RunPod provides two connection methods:
1. `ssh [pod-id]@ssh.runpod.io -i ~/.ssh/id_ed25519` (Recommended)
2. `ssh root@[ip] -p [port] -i ~/.ssh/id_ed25519` (Direct connection)

Use the first one initially. If it fails, try the second.

## tmux Not Installed
```bash
bash: tmux: command not found
```
**Solution**:
```bash
apt update && apt install -y tmux
```

## File Transfer Issues

### rsync Fails with "unexpected tag" Error
```bash
rsync(11700): error: unexpected tag 25 (0x2072756f)
```
**Solution**: Use scp instead:
```bash
# Method 1 (using RunPod SSH gateway)
scp -r -i ~/.ssh/id_ed25519 hand_cls [pod-id]@ssh.runpod.io:/workspace/

# Method 2 (direct connection)
scp -r -P [port] -i ~/.ssh/id_ed25519 hand_cls root@[ip]:/workspace/
```

### scp "subsystem request failed"
If the first scp method fails with:
```bash
subsystem request failed on channel 0
scp: Connection closed
```
**Solution**: Use the direct IP method (Method 2 above)

### Internal IP in Setup Script
The setup script shows an internal IP like `172.18.0.2`. 
**Solution**: Ignore this IP. Use the connection strings from RunPod dashboard.

## Dataset Upload Commands

### ❌ Wrong (Don't run on RunPod):
```bash
# This won't work - rsync not installed on RunPod
root@pod:/# rsync -avh hand_cls/ root@172.18.0.2:/workspace/hand_cls/
```

### ✅ Correct (Run from LOCAL terminal):
```bash
# Navigate to workshop directory first
cd "/Users/[username]/path/to/finetune-workshop"

# Then upload using your pod's connection info
scp -r -P [port] -i ~/.ssh/id_ed25519 hand_cls root@[ip]:/workspace/
```

## Common Mistakes

### Running Upload Commands on Wrong Terminal
- **Upload commands** → Run on your LOCAL Mac terminal
- **Training commands** → Run on RunPod SSH session
- Keep both terminals open!

### Missing Dataset
Before uploading, ensure you have:
```bash
# On LOCAL terminal
python3 create_dataset_structure.py
# Add images to folders
python3 create_dataset_structure.py check
```

### Wrong Working Directory
Always run commands from the workshop directory:
```bash
cd "/Users/[username]/Dev/Active Projects/finetune-workshop"
```

## Quick Checklist

1. ✅ SSH key added to RunPod settings
2. ✅ Pod created with PyTorch 2.4 + CUDA 12.4
3. ✅ Connected via SSH (accepted fingerprint)
4. ✅ tmux installed and session started
5. ✅ Setup script run successfully
6. ✅ Dataset created locally
7. ✅ Dataset uploaded via scp (from LOCAL terminal)
8. ✅ Ready to train!

## Pro Tips

- Use tmux to keep training alive: `tmux new -s workshop`
- Write down your pod connection info
- Keep local and RunPod terminals clearly labeled
- Test with small dataset first (20-50 images)
- Use direct IP connection if RunPod SSH gateway fails