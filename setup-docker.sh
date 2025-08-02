#!/bin/bash

# Setup script for InterpelBot Docker deployment

echo "🐳 Setting up InterpelBot Docker environment..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 data logs

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json and update configuration:"
echo "   - mattermost_webhook_url"
echo "   - sejm_term"
echo "   - mps (list of MPs with their IDs and Mattermost users)"
echo "2. Run: docker-compose up -d"
echo "3. Check logs: docker-compose logs -f"
echo ""
echo "The bot will run every hour automatically." 