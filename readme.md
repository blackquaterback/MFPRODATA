# 🧠 eparse — Mutual Fund Portfolio Parser

`eparse` is a foundational tool built to extract and normalize portfolio disclosures and NAV data from multiple Indian Mutual Fund AMCs. Given the lack of standardization in disclosure formats across AMCs, this library uses custom parsing logic per AMC to create a consistent structured format.

---

## 🚧 Refactoring in Progress

The current implementation of `eparse` is being refactored to improve maintainability, scalability, and clarity. The upcoming changes include:

### ✅ Goals for Refactoring

- **Introduce Object-Oriented Structure**  
  Transition to an extensible architecture using an **abstract base class** for portfolio parsing logic.

- **AMC-Specific Parsers**  
  Each AMC will have its own subclass implementing a standard interface (`extract_portfolio()`, `extract_nav()` etc.).

- **Use Python 3.10+ `match-case` for Parsing Variants**  
  Where applicable, `match-case` will be used to simplify branching logic for parsing subtle variations in formats.

- **Add Tests and Validation**  
  Include test cases and example files for each supported AMC (e.g., Parag Parikh, HDFC, Axis, etc.) to improve reliability.

---

## 🧩 Proposed Class Structure

```python
from abc import ABC, abstractmethod

class FundParser(ABC):
    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def extract_portfolio(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def extract_nav(self) -> pd.DataFrame:
        pass
