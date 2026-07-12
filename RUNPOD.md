# Remote GPU (RunPod) setup

Full from-scratch steps for renting a GPU pod, installing LM Studio on it, and
connecting this project's `main.py` (which runs locally on your Mac) to it
over an SSH tunnel. Follow these in order after terminating a previous pod.

---

## 1. Rent a pod

1. Go to [runpod.io](https://runpod.io) → **Pods** → **Deploy**.
2. GPU: search for **RTX A6000** (48GB VRAM, ~$0.49/hr). Comfortably fits a
   7B–35B vision model with room to spare.
3. Template: any basic Linux/Ubuntu community template — doesn't matter much,
   LM Studio gets installed manually on top either way.
4. Container disk: bump to **~50GB** (room for model weights).
5. Click **Deploy**, wait ~1-2 min until status shows **Running**.

You need at least 1 hour's worth of credit loaded on your account to deploy
an on-demand pod (Billing page → add credit).

---

## 2. SSH access

To skip the key-propagation issue from last time: add your public key to
your RunPod **account** (top-right icon → Settings → SSH Public Keys) —
**before** deploying the pod, since RunPod only injects it at boot time. If
the pod is already running when you add the key, it won't take effect.

Your existing local key (reuse this, no need to regenerate):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP9igtaNfNc7XR82Cgh6kb6yZsjLClEHxUCfNbv2XBaC 2123759@stud.hs-mannheim.de
```

If SSH still refuses the key after deploy (permission denied), fall back to
the pod's **Web terminal** (toggle it on in the pod's Connect panel — no key
needed) and add the key manually from inside the container:
```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP9igtaNfNc7XR82Cgh6kb6yZsjLClEHxUCfNbv2XBaC 2123759@stud.hs-mannheim.de" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
service ssh status   # confirm sshd is running
```

Once it's working, get the exact SSH command from the pod's **Connect** panel
— use **"SSH over exposed TCP"** (`ssh root@<ip> -p <port> -i ~/.ssh/id_ed25519`),
not the `ssh.runpod.io` proxy form — the direct form is required for port
forwarding later. The IP/port change per pod, copy them fresh each time.

---

## 3. Install LM Studio (headless) on the pod

SSH in, then run:
```bash
curl -fsSL https://lmstudio.ai/install.sh | bash
export PATH="/root/.lmstudio/bin:$PATH"
lms daemon up
```

---

## 4. Download and load a vision-capable model

```bash
lms get qwen3.6-35b-a3b
```
(Or search interactively with `lms get` alone if the exact name doesn't match.)

Load it with a bigger context and enough parallel slots — **do not use plain
`lms load`**. LM Studio's default (8192 ctx split across 4 slots) is too
small per-slot for page-image requests and causes 400 "context size
exceeded" errors as soon as more than one request runs concurrently:
```bash
lms load qwen/qwen3.6-35b-a3b --gpu=max --context-length 32768 --parallel 4 -y
```

Confirm it loaded with the right settings:
```bash
lms ps
# should show CONTEXT 32768, PARALLEL 4
```

Note the exact identifier `lms ps` reports (e.g. `qwen/qwen3.6-35b-a3b`) —
that's what goes in the `-m` flag below.

---

## 5. Start the API server

```bash
lms server start --port 1234
```

Sanity check from inside the pod:
```bash
curl http://127.0.0.1:1234/v1/models
```

---

## 6. Tunnel from your Mac

In its own terminal tab on your Mac (leave it running, no output is normal):
```bash
ssh -N -o ExitOnForwardFailure=yes -L 1234:localhost:1234 root@<pod-ip> -p <pod-ssh-port> -i ~/.ssh/id_ed25519
```
Replace `<pod-ip>` / `<pod-ssh-port>` with this pod's values from step 2.

Verify the tunnel from a second Mac terminal tab:
```bash
curl http://127.0.0.1:1234/v1/models
```

---

## 7. Run a conversion

In a separate tab, from the project directory (`cd` into `PDF2MD` first —
running this from the wrong directory, e.g. the pod's shell, gives a
"can't open file '//main.py'" error):
```bash
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result.md -s adaptive \
  -m "qwen/qwen3.6-35b-a3b" -c 4
```

Swap `-i`/`-o` for the other PDFs as needed:
```bash
python3 main.py -i "pdf_source/A_human_in_the_loop_system_for_research_paper_generation_using_local_large_language_models.pdf" \
  -o output/hitl_thesis.md -s adaptive -m "qwen/qwen3.6-35b-a3b" -c 4

python3 main.py -i pdf_source/Bachelor_Thesis_Informatik_Koehler_Sven.pdf \
  -o output/koehler_thesis.md -s adaptive -m "qwen/qwen3.6-35b-a3b" -c 4
```
Run them one at a time, not together — they'd compete for the same GPU.

If your Mac needs to stay awake for a long run without the lid open, prefix
the command with `caffeinate`.

---

## 8. When done

**Terminate** the pod (not just Stop) from the RunPod dashboard. This
project's pods have no persistent `/workspace` volume, so Stop erases the
container disk anyway (same data loss as Terminate) while still charging you
for volume storage you don't have — Terminate is strictly better and stops
all billing immediately.
