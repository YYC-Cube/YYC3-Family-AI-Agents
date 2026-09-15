#!/bin/bash
# 从节点分布式推理启动脚本 (yyc3-102)
# 基于PyTorch + NeMo容器，与主节点协同工作

docker run --gpus all -it --rm \
  -v /mnt/nas/qa_data:/workspace/data \
  --network host \
  nvcr.io/nvidia/nemo:latest \
  python -m torch.distributed.run \
  --nproc_per_node=2 \
  --nnodes=2 \
  --node_rank=1 \
  --master_addr="192.168.3.101" \
  --master_port=12345 \
  /workspace/scripts/enterprise_qa_inference.py \
  --data_dir /workspace/data \
  --model_path /workspace/models/enterprise_llm.pt
