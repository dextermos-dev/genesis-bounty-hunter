# Compact <=4KB Stack VM with Fiber Checkpointing (t=19)
import json, time

NOP, PUSH, POP, DUP, SWAP = 0, 1, 2, 3, 4
ADD, SUB, MUL, DIV, MOD = 10, 11, 12, 13, 14
EQ, LT, GT, JMP, JZ, JNZ = 20, 21, 22, 30, 31, 32
CALL, RET, INTR, HALT = 40, 41, 50, 99

GAS = {0:1, 1:2, 2:1, 3:2, 4:2, 10:3, 11:3, 12:5, 13:7, 14:7,
       20:2, 21:2, 22:2, 30:3, 31:4, 32:4, 40:10, 41:6, 50:1, 99:0}

class VMError(Exception): pass
class FiberVM:
    def __init__(self, code, gas=1_000_000):
        self.code, self.gas, self.ip = code, int(gas), 0
        self.stack, self.call_stack = [], []
        self.halted, self.interrupted = False, False

    def checkpoint(self) -> str:
        return json.dumps({
            'ip': self.ip, 'stack': self.stack, 'call_stack': self.call_stack,
            'gas': self.gas, 'halted': self.halted, 'interrupted': self.interrupted
        })

    @classmethod
    def restore(cls, code, cp: str) -> 'FiberVM':
        d = json.loads(cp)
        vm = cls(code, gas=d['gas'])
        vm.ip, vm.stack, vm.call_stack = d['ip'], d['stack'], d['call_stack']
        vm.halted, vm.interrupted = d['halted'], d['interrupted']
        return vm

    def step(self):
        if self.halted or not (0 <= self.ip < len(self.code)):
            self.halted = True
            return False
        inst = self.code[self.ip]
        op, arg = inst if isinstance(inst, (list, tuple)) else (inst, None)
        cost = GAS.get(op, 1)
        if self.gas < cost: raise VMError("OOG")
        self.gas -= cost

        if op == NOP: self.ip += 1
        elif op == PUSH: self.stack.append(int(arg)); self.ip += 1
        elif op == POP: self.stack.pop(); self.ip += 1
        elif op == DUP: self.stack.append(self.stack[-1]); self.ip += 1
        elif op == SWAP: self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]; self.ip += 1
        elif op in (ADD, SUB, MUL, DIV, MOD):
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append((a+b) if op==ADD else (a-b) if op==SUB else (a*b) if op==MUL else (a//b) if op==DIV else (a%b))
            self.ip += 1
        elif op in (EQ, LT, GT):
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(1 if (op==EQ and a==b) or (op==LT and a<b) or (op==GT and a>b) else 0)
            self.ip += 1
        elif op == JMP: self.ip += int(arg)
        elif op in (JZ, JNZ):
            cond = self.stack.pop()
            self.ip = self.ip + int(arg) if (op==JZ and cond==0) or (op==JNZ and cond!=0) else self.ip + 1
        elif op == CALL: self.call_stack.append(self.ip + 1); self.ip = int(arg)
        elif op == RET: self.ip = self.call_stack.pop()
        elif op == INTR: self.interrupted = True; self.ip += 1; return False
        elif op == HALT: self.halted = True; return False
        else: raise VMError(f'Unknown op: {op}')
        return True

    def run(self, max_steps=None):
        steps = 0; self.interrupted = False
        while not self.halted:
            if max_steps is not None and steps >= max_steps:
                self.interrupted = True
                break
            if not self.step(): break
            steps += 1
        return steps

def run_tests():
    code = [(PUSH, 10), (PUSH, 20), (ADD, None), (PUSH, 2), (MUL, None),
            (PUSH, 15), (SUB, None), (PUSH, 3), (DIV, None), (CALL, 11), HALT,
            (DUP, None), (MUL, None), (RET, None)]
    vm = FiberVM(code, gas=10000); vm.run()
    assert vm.stack == [225]

    vm1 = FiberVM(code, gas=10000)
    s1 = vm1.run(max_steps=7); cp = vm1.checkpoint()
    vm2 = FiberVM.restore(code, cp)
    s2 = vm2.run()
    assert vm2.stack == [225]

    bench = [(PUSH, 50_000), (PUSH, 1), (SUB, None), (DUP, None), (JNZ, -3), HALT]
    vm_b = FiberVM(bench, gas=10_000_000)
    t0 = time.perf_counter()
    steps = vm_b.run()
    dur = time.perf_counter() - t0
    ops = steps / dur if dur > 0 else 0
    print(f'[PASS] Tests & Round-trip passed ({s1}+{s2} steps). {steps:,} ops in {dur:.4f}s ({ops:,.0f} ops/sec)')
    return ops

if __name__ == '__main__':
    run_tests()
