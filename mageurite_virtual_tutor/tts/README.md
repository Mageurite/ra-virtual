# How to Use the TTS Module

Need a Chinese version? [Click here](README_CN.md).

## Composition of tts Directory

``` sh
tts/
├── .gitignore
├── model_1/                          
├── model_2/                         
├── model.../                         
├── documents/  
│   ├── user_manual.md                         
│   ├── api_document.md              
│   └── technical_doc.md
├── requirements/
├── test/
│   ├── templates/                
│   │   └── index.html            
│   ├── main.py                   
│   └── start_up.sh   
├── readme.md
├── config.json                     # TTS service configuration file (pid, port, etc.)
├── model_info.json                 # Model metadata (environment, parameters, startup path, configs, etc.)
├── tts.py                          # Main program, handles TTS requests (unified interface)
└── cmd_list.sh                     # Quick startup script (launches the entire TTS system)
```

-   `model_xx`: Folder name equals model name, stores all related files
    of a specific model, including configs, model weights, pretrained
    parameters, datasets, control code, and utility scripts.\
-   `documents`: TTS-related documents, including user manual, technical
    documents, test reports, and API docs.\
-   `requirements`: Stores environment configuration files.\
-   `test`: TTS-related test code and results, separated into frontend
    and backend.\
-   `fast_startup.sh`: Quick startup script for TTS service (not
    runnable in current version).\
-   `config.json`: TTS service configuration file (pid, port, etc.).\
-   `model_info.json`: Model metadata (environment, parameters, startup
    path, configs, etc.).\
-   `tts.py`: Main TTS program, handles TTS requests (unified
    interface).

## How to Use TTS

### Entry Program

``` sh
cd tts
uvicorn tts:app --host 0.0.0.0 --port 8204
```

After switching to the `tts` directory, use `uvicorn` to start the TTS
process.

### Quick Start

1.  Install dependencies
    -   Install conda (Anaconda or Miniconda)
    -   Install Python 3.8+
    -   Install environment for each model (Replace MODEL_NAME with
        actual name, e.g., `sovits`)

    ``` bash
    conda env create -f requirements/base/environment.yml
    conda env create -f requirements/MODEL_NAME/environment.yml 
    ```
2.  Execute quick startup command to start TTS service

``` bash
uvicorn tts:app --host 0.0.0.0 --port 8204
```

## Model Explanation

### Client-API

#### Overview

This API is provided by the client, only supports fixed voice
generation, no fine-tuning.

Each gender provides 5 voices (`f0–f4` for female, `m0–m4` for male),
selectable via parameters.

**API validity must be specified by the client.**

#### Principle

Call server-deployed TTS system via RESTful interface, returns audio in
`.wav` format.

#### API Example

``` py
requests.post(
    "http://216.249.100.66:13645/v1/audio/speech",
    json={
        "input": text,         # text to synthesize
        "voice": voice         # voice, e.g. f0–f4 or m0–m4
    }
)
```

#### File Structure

``` sh
client_api/
├── output/
│   ├── output_male1.wav
│   ├── output_male2.wav
│   └── res.log
├── env.sh
├── client.py
└── rtf_client.txt
```

------------------------------------------------------------------------

### EdgeTTS-API

#### Overview

-   Python wrapper `edge-tts` for Microsoft Edge internal TTS service\
-   Supports multilingual, multi-voice synthesis\
-   Supports streaming output

#### Principle

Call Microsoft TTS backend via EdgeTTS SDK. Supports stream synthesis +
playback.

#### API Example

``` py
import edge_tts

communicate = edge_tts.Communicate(text, character="en-US-GuyNeural")
await communicate.save("output.wav")
```

#### File Structure

``` sh
edge/
├── logs/       # stores running logs
│   ├── ...
├── output/     # stores temporary outputs
│   ├── ...
├── env.sh
├── server.py
├── edge.py
└── start.sh
```

------------------------------------------------------------------------

### Tacotron2

#### Overview

Tacotron2 is an end-to-end deep learning-based TTS system by Google.
Combines Seq2Seq, attention mechanism, and vocoders (e.g., WaveGlow) for
high-quality synthesis.

-   Does **not** support voice switching\
-   Does **not** support one-shot cloning

#### Principle

1.  Text → Spectrogram: encoder-decoder predicts Mel-spectrogram.\
2.  Spectrogram → Audio: vocoder (e.g., WaveGlow, Griffin-Lim)
    reconstructs waveform.

#### Reference

-   [Natural TTS synthesis by conditioning WaveNet on Mel spectrogram
    predictions (Google, 2017)](https://arxiv.org/abs/1712.05884)

#### File Structure

``` sh
taco/
├── server.py
├── env.sh
└── start.sh
```

------------------------------------------------------------------------

### Cosyvoice2-0.5B

#### Overview

CosyVoice is a Transformer-based large-scale TTS model. Cosyvoice2-0.5B
is a lightweight version (500M parameters).

-   Supports one-shot cloning\
-   Generates natural speech

#### Principle

-   Uses self-supervised pretraining + TTS fine-tuning.\
-   Combines phoneme encoder + Mel decoder, supports multi-speaker
    synthesis.\
-   Built-in vocoder generates waveform during inference.

#### File Structure

``` sh
cosyvoice2/
├── env.sh
├── logs/   
│   ├── ...
├── output/ 
│   ├── ...
└── Cosyvoice/
    ├── pretrained_model/   
    │   ├── CosyVoice-300M/
    │   └── CosyVoice2-0.5B/
    ├── ...
    ├── server.py       # entrypoint for audio generation
    ├── cosy_05.py
    ├── cosy_300.py
    └── start.sh        # server startup script
```

------------------------------------------------------------------------

### GPT-SoViTs

#### Overview

GPT-SoVITS combines So-VITS and GPT architectures into a new-gen
TTS/VITS model. Supports fast speaker adaptation with few samples.

-   Supports one-shot cloning

#### Principle

-   Text → Speech Representation: GPT encodes text to generate acoustic
    features.\
-   Speech Representation → Audio: So-VITS produces high-quality
    synthesis.\
-   Includes speaker encoder, automatic aligner, etc.

#### File Structure

``` sh
sovits/
├── env.sh
├── logs/   
│   ├── ...
├── output/ 
│   ├── ...
└── GPT-SoVITS/
    ├── GPT_SoVITS/     # model parameters & related files
    ├── server.py       # audio generation entrypoint
    └── start.sh        # server startup script
```

------------------------------------------------------------------------

## Change Log

-   6.13
    -   Create TTS readme file\
-   6.16
    -   Test client API\
-   6.17
    -   Client API RTF statistics\
-   6.20
    -   Tacotron2 demo 1\
    -   Tacotron2 test_log\
-   6.21
    -   VITS-Fast demo 1\
-   6.22
    -   VITS-Fast demo 2\
-   6.23
    -   CosyVoice - 0.5B\
-   6.24
    -   CosyVoice - 0.5B rtf\
-   6.25
    -   CosyVoice - rtf_log\
-   6.27
    -   Cosy server\
    -   fast_startup\
-   6.28
    -   EdgeTTS API\
    -   rtf\
-   6.29
    -   Edge server\
    -   Edge startup\
-   7.1
    -   soViTs demo1\
    -   rtf of soViTs\
-   7.2
    -   Update readme.md\
    -   Standardize file naming rules\
-   7.5
    -   Taco server supports pitch change via playback speed adjustment\
-   7.6
    -   Taco server supports pitch shift without duration change\
-   7.8
    -   Taco server basically complete\
-   7.11
    -   Draft user manual framework\
    -   Draft technical document framework\
    -   Draft TTS API doc 1.0\
-   7.13
    -   Improve CosyVoice response speed\
    -   Cosy server basically complete\
-   7.15
    -   Add warm-up to soViTs\
    -   Sovits server basically complete\
    -   Edge server final version\
-   7.16
    -   Use relative paths instead of absolute paths for model startup\
-   7.18
    -   Unified TTS server for startup, inference, and config query\
-   7.19
    -   Access TTS server via API\
-   7.21
    -   Server supports API-based avatar process switching\
-   7.23
    -   Write model switch frontend demo\
    -   Test remote call for model switching\
    -   Update model switch demo\
-   7.24
    -   Merge recent updates\
-   7.26
    -   Update user manual\
    -   Update technical document\
    -   Update API document\
-   7.28
    -   Avatar-based model switching\
    -   Complete avatar API base structure\
-   7.29
    -   Complete avatar API\
    -   Complete avatar test demo\
-   7.31
    -   Complete avatar frontend demo\
    -   Add avatar section to documents\
-   8.2
    -   Integrate frontend demo into admin page\
    -   Update user manual\
-   8.3
    -   Update technical doc\
    -   Update API doc\
    -   Complete admin page test\
-   8.4
    -   Integrate avatar switching into user homepage\
    -   Complete avatar switching test\
-   8.5
    -   Update user manual\
    -   Update technical doc\
    -   Update API doc
