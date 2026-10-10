"""Create the StreetSignal Colab demo notebook (deploy/colab/streetsignal-colab.ipynb).

Run from anywhere:
    python deploy/colab/make_colab_notebook.py

The notebook boots Ollama + qwen2.5vl:3b inside a Colab session, clones the
public repo, launches the app with STREET_SIGNAL_HOST_MODE=cloud, and prints
a temporary public trycloudflare.com URL.
"""

import json
from pathlib import Path

NOTEBOOK_TITLE = [
    "# 🌱 StreetSignal — free public demo (Colab + tunnel)",
    "",
    "Runs the whole app — Streamlit UI, Ollama, and the vision model `qwen2.5vl:3b` — inside this Colab session, then prints a temporary public URL anyone can open.",
    "",
    "**How to use:**",
    "1. `Runtime → Run all` (or run the cells in order).",
    "2. The **last code cell prints the public URL** — open it, or share it while the session lives.",
    "3. Keep this tab open: the demo URL and everything in it die when the session stops or is idle too long.",
    "",
    "**Notes:**",
    "- Any runtime works (CPU is fine; a T4 GPU makes analysis faster). First setup takes ~5 minutes; later sessions re-download the 2.2 GB model (Colab disk is not persistent).",
    "- This is a **demo link, not a permanent deployment**: the URL changes every session, and it may take ~30 seconds to respond on first visit.",
    "- Privacy mode is `STREET_SIGNAL_HOST_MODE=cloud`: photos sent through the public link are analyzed by the Ollama model running **in this session** — never sent to any third-party AI API — and reports leave the app only by downloading the JSON.",
]

CODE_CELLS = [
    (
        "cell-ollama-install",
        [
            "# 1 · Install Ollama into this session",
            "!curl -fsSL https://ollama.com/install.sh | sh",
        ],
    ),
    (
        "cell-ollama-pull",
        [
            "# 2 · Start the Ollama server and pull the vision model (~2.2 GB, one time per session)",
            "!(nohup ollama serve >/dev/null 2>&1 &)",
            "!for i in $(seq 1 30); do curl -s http://localhost:11434/ >/dev/null && break || sleep 1; done",
            "!ollama pull qwen2.5vl:3b",
        ],
    ),
    (
        "cell-app",
        [
            "# 3 · Get the app (clones the public repo) and install its Python deps",
            "!rm -rf /content/streetsignal",
            "!git clone --depth 1 https://github.com/archita404/streetsignal /content/streetsignal",
            "!pip install -q -r /content/streetsignal/requirements.txt",
        ],
    ),
    (
        "cell-cloudflared",
        [
            "# 4 · Install cloudflared (WebSocket-capable tunnel, no account needed)",
            "!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared",
            "!chmod +x /usr/local/bin/cloudflared",
            "!cloudflared --version",
        ],
    ),
    (
        "cell-streamlit",
        [
            "# 5 · Run the StreetSignal app in privacy mode for cloud demos",
            "!cd /content/streetsignal && (STREET_SIGNAL_HOST_MODE=cloud nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false >/dev/null 2>&1 &)",
            "!sleep 10",
            '!curl -s -o /dev/null -w "Streamlit status: %{http_code}\\n" http://localhost:8501',
        ],
    ),
    (
        "cell-tunnel",
        [
            "# 6 · Open the public tunnel — the printed URL is your demo link",
            "!(nohup cloudflared tunnel --url http://localhost:8501 --no-autoupdate > /content/tunnel.log 2>&1 &)",
            "!sleep 15",
            "!grep -oE 'https://[a-z0-9-]+\\.trycloudflare\\.com' /content/tunnel.log | head -n 1",
        ],
    ),
]

TROUBLESHOOTING = [
    "## If something looks off",
    "- **No URL printed above** → re-run the tunnel cell (the 15-second wait is sometimes too short). If Streamlit printed status `000` instead of `200`, re-run the Streamlit cell first, then the tunnel cell.",
    "- **Public link slow on first open** → normal: the tunnel warms up and the first render compiles. Give it ~30 seconds.",
    "- **Analysis takes long** → expected on CPU; `Runtime → Change runtime type → T4 GPU` makes it noticeably faster (then re-run all cells).",
    "- **Session died / URL stopped working** → Colab reclaims idle sessions; run all cells again and share the new URL.",
]

METADATA = {
    "accelerator": "GPU",
    "colab": {"name": "StreetSignal demo", "provenance": []},
    "kernelspec": {"display_name": "Python 3", "name": "python3"},
    "language_info": {"name": "python"},
}


def make_notebook():
    cells = [
        {
            "cell_type": "markdown",
            "id": "cell-title",
            "metadata": {},
            "source": NOTEBOOK_TITLE,
        }
    ]
    for cell_id, lines in CODE_CELLS:
        cells.append(
            {
                "cell_type": "code",
                "execution_count": None,
                "id": cell_id,
                "metadata": {},
                "outputs": [],
                "source": lines,
            }
        )
    cells.append(
        {
            "cell_type": "markdown",
            "id": "cell-troubleshoot",
            "metadata": {},
            "source": TROUBLESHOOTING,
        }
    )
    return {
        "cells": cells,
        "metadata": METADATA,
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main():
    target = Path(__file__).with_name("streetsignal-colab.ipynb")
    target.write_text(
        json.dumps(make_notebook(), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"OK {target}")


if __name__ == "__main__":
    main()
