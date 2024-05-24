# CA-Experiment

asm | risc | harv | mc | instr | binary | stream | mem | cstr | prob2

## Command Binary Representation (32-bit)

| Opcode | RB   | R1 | Address/Number/R2 | Flag | Operation                |
|--------|------|------------------|----------------|------|--------------------------|
| 7 bits | 4 bits | 4 bits         | 16 bits        | 1 bit|           = 32 bit       |
| Opcode | RB   | 0000             | Address        | 1    | Write word operation     |
| Opcode | RB   | R1               | 16 * [0]       | 0    | Load word operation      |
| Opcode | RB   | R1               | R2             | 0    | Math operations (reg-reg)|
| Opcode | RB   | R1               | Number         | 1    | Math operations (reg-imm)|
| Opcode | RB   | R1               | Address        | 0    | Branch operations        |
| Opcode | 0000 | 0000             | Address        | 1    | Branch (Jump) operation  |
| Opcode | 0000 | 0000             | 16 * [0]       | 0    | HALT/NOP operation       |
