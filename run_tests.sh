#!/bin/bash
# Test runner script that ensures virtual environment is activated

# Check if we're already in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment already activated: $VIRTUAL_ENV"
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run tests with the specified arguments
python -m pytest "$@"
