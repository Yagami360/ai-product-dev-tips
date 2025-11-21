#!/bin/bash

# セーフティー処理: DGXサーバーではpoweroffしない
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *"dgx"* ]] || [[ "$HOSTNAME" == *"DGX"* ]]; then
    echo "⚠️  Warning: DGX server detected (hostname: $HOSTNAME)"
    echo "⚠️  Poweroff is disabled for safety reasons on DGX servers."
    echo "Starting training without poweroff..."
    make train
    echo "✅ Training completed. Server will NOT be powered off."
else
    echo "Starting training with auto-poweroff..."
    make train
    echo "Training completed. Powering off in 60 seconds..."
    echo "Press Ctrl+C to cancel poweroff."
    sleep 60
    sudo poweroff
fi
