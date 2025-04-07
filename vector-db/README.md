# ChromaDB Setup

## Considerations
We will be using vector DB through ChromaDB. While ChromaDB can work using backend FastAPI, we have 2 main concerns:
- Computational Demand: Would the backend be enough, given Railway only offers 5 GB?
- Deployment Concerns: Would redeployments erase the stored vectors & metadata?

## Approach
Our minimal approach is to implement GCP VM to host ChromaDB. We simply have to create ChromaDB instance, mount it to a persistent disk, host it in a minimal VM and expose the vm through the IP address. 


### Setting Up the VM
To start, the vm has to run the ChromaDB. We used the following startup script.
The key components are ChromaDB (of course~) and [Cloudflare Tunneling](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
``` sh
sudo apt update && sudo apt install -y python3 python3-pip curl python3.11-venv

sudo python3 -m venv ~/python-kernel

sudo source ~/python-kernel/bin/activate

sudo pip install chromadb

# Install Cloudflare Tunnel
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

# Assuming the data disk is new and attached, do
sudo mkdir /mnt/chroma_data
sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb # Formating disk
sudo mount -o discard,defaults /dev/sdb /mnt/chroma_data

# Run ChromaDB
sudo chown -R <your-alias>:<your-alias> /mnt/chroma_data ## granting you full ownership over the disk
nohup chroma run --path /mnt/chroma_data > ~/chroma_db.log 2>&1 & ## ChromaDB is running, happy

# Login through Cloudflare
cloudflared tunnel login

# Create a Cloudflare Tunneling Configuration File
vim ~/.cloudflared/config.yml ## See below for how this file should look

# Create Tunnel 
cloudflared tunnel create chroma-tunnel

# Tunneling using Cloudflare
nohup cloudflared tunnel run chroma-tunnel > cloudflared.log 2>&1 &
```
Then the ChromaDB is up on `https://chroma.sanvia.app`

### Yaml File Configuration for Tunneling
Reference (configuration file): [Configuration File](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/local-management/configuration-file/)
``` yml
tunnel: chroma-tunnel
credentials-file: <your credential json files, probably under .cloudflared>

ingress:
    - hostname: chroma.sanvia.app
      service: http://localhost:8000
    - service: http_status:404
```

### Access Control
We added an extra layer of protection using API Key through Cloudflare. Any request going to https://chroma.sanvia.app would require the API key.

### Testing
``` sh
curl -X GET https://chroma.sanvia.app/api/v2/heartbeat \
  -H "CF-Access-Client-Id: <client_id>" \
  -H "CF-Access-Client-Secret: <token-that-you-saved>"
```