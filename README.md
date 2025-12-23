# Jefferson - Warframe Discord Bot

A comprehensive Discord bot for Warframe players, providing real-time game information, market data, and other utility commands.

# WORK IN PROGRESS

## Features

### Commands


## Quick Start

### Prerequisites
- Python 3.9+
- Redis server
- Discord Bot Token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aldi-f/jefferson-backend.git
cd jefferson-backend
```

2. **Install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up Redis**
```bash
# Using Docker (recommended)
docker run -d --name redis_jeff -p 6378:6378 redis:trixie

# Or install Redis locally
# Follow Redis installation instructions for your OS
```

5. **Run the bot**
```bash
# Run all services (bot + web API)
python -m app.main

# Run only the Discord bot
python -m app.bot.main

# Run a specific job
python -m app.main job load_wiki
```

### Docker Deployment

**Build and run with Docker Compose**
```bash
docker-compose up -d
```


## Configuration

### Discord Bot Setup

1. **Create a Discord Application**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Give it a name and agree to terms

2. **Create a Bot User**
   - Go to "Bot" tab
   - Click "Add Bot"
   - Enable "Message Content Intent"
   - Copy the bot token

3. **Invite the Bot**
   - Go to "OAuth2" → "URL Generator"
   - Select scopes: `bot` and `applications.commands`
   - Select permissions needed for your server
   - Copy the generated URL and invite the bot

## Command Usage

### Basic Commands
```
/alerts              - Show current alerts with rewards
/pricecheck <item>   - Check market prices for items
/fissures           - Show active void fissures  
/sortie             - Display daily sortie missions
/nightwave          - Show current nightwave challenges
/baro               - Void trader inventory and location
/circuit            - Steel Path circuit information
/archon             - Weekly archon hunt details
/darvo              - Current Darvo deals
/ping               - Check bot latency
/help               - Show help information
```

### Market Commands
```
/pricecheck soma prime - Check prices for Soma Prime
/pricecheck lightning stance - Check mod prices
```

### Information Commands
```
/profile <username> - Player profile information
/relic lith a1       - Relic reward information
/riven dread         - Riven mod data
/weapons kuva lich  - Weapon statistics
/warframe mirage    - Warframe abilities
/mods hornet strike - Mod information
/arcanes magus elevate - Arcane effects
```


## Troubleshooting

### Debug Mode
Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
WEB_DEBUG=true
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
