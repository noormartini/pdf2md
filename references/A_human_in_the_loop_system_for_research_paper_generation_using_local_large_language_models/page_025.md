this approach, the interaction flow between the user and the system, key design decisions,
and their implications.
Motivation
The HITL strategy is motivated by known problems of running LLMs locally
on consumer hardware. As explained in Chapter 2, the most powerful LLMs are propri-
etary and cannot be run by end users. The best open-weight models still rank below the
top proprietary models on benchmarks [17], so local inference may produce lower quality
results.
Running an LLM locally requires enough memory to hold the model weights and the
inference context [18]. The largest open-weight models have hundreds of billions of pa-
rameters, for example DeepSeek-V33 with 671 billion or Qwen3.54 with 397 billion. Their
weights at half or full precision need hundreds of gigabytes or more of VRAM or RAM
or a combination of both. At two bytes per parameter, DeepSeek-V3’s weights alone need
around 1.3 TB of memory and Qwen3.5-397B-A17B’s around 800 GB. In practice, end
users might be limited to smaller or quantized variants that fit on their hardware. While
quantization at moderate levels (for example 8-bit) can preserve most of a model’s perfor-
mance, it is a tradeoff that may reduce the quality of answers [19].
A further risk is error propagation. In a multi-stage research workflow, the output of each
phase serves as the input for the next. If the model hallucinates and produces a factual
error at an early stage, this mistake could carry over into all following phases [8]. LLMs
cannot reliably self-correct such errors without external feedback [48].
A fully agentic pipeline was considered as an alternative design, where the model plans and
executes all phases autonomously without any user intervention. This implies the need for
reliable tool calling, where the model selects the correct tool with the correct parameters
at each step. Models that end users can run locally might not support tool calling, and
those that do cannot guarantee correct tool calls, since LLMs are probabilistic [14]. Each
autonomous step would therefore be a new source of error on top of the error propagation
risk described above.
The system addresses these risks by pausing after each phase so the user can verify the
output before the next phase runs. Since LLMs cannot reliably self-correct on their own
yet, the user can take over that role. The result is a division of labor where the system
generates the initial content and the user can check its correctness.
Interaction Flow
Figure 4.2 shows this division of labor between the user and the system.
In this flow the system never just continues on its own. Every progression depends on the
3https://huggingface.co/deepseek-ai/DeepSeek-V3
4https://huggingface.co/Qwen/Qwen3.5-397B-A17B
15