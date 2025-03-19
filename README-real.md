# Local LLM Demo - Real Model Implementation

This branch extends the basic demo to use an actual language model (TinyLlama-1.1B) that runs completely locally in Docker.

## Features

- Real language model (TinyLlama-1.1B-Chat)
- Conversation memory (maintains context)
- Completely local execution
- No data leaves your environment
- No external API calls

## Requirements

- Docker and Docker Compose
- At least 4GB of available RAM
- ~2GB of disk space (for the model)

## Usage

```bash
# Build and start the container
docker-compose -f docker-compose.real.yml up --build

# Access the interface
# Open http://localhost:7860 in your browser
```

## First Run

On the first run, the container will download the model from Hugging Face. This might take a few minutes depending on your internet connection. Subsequent runs will be faster as the model is cached.

## Model Details

- **Model**: TinyLlama-1.1B-Chat-v1.0
- **Size**: ~2GB
- **Architecture**: Transformer-based language model
- **Context Window**: 2048 tokens
- **Language Support**: English

## Customization

To use a different model, edit the `model_id` variable in `app_real.py`. Some alternatives:

- `microsoft/phi-2` (2.7B parameters)
- `google/gemma-2b-it` (2B parameters) 
- `facebook/opt-1.3b` (1.3B parameters)

Be aware that larger models will require more RAM.

## Security Considerations

- All processing happens locally
- No data is sent to external servers
- Model weights are downloaded once and cached
- No API keys required

## Production Use

This demo is for testing/demonstration purposes only. For production use, consider:

- Adding authentication
- Implementing rate limiting
- Adding logging and monitoring
- Optimizing for performance
- Using quantized models for better performance
