# architect-drawing

## Description
Base module for Tracepath on AQL platform. Reads from json file.

---

## To run

### Build Image
```bash
docker build --target runtime -t drawing .
```
### Run Image
```bash
docker run -ti --rm -w /app -v ./output:/app/output drawing bash
```

---

## Helpful commands

### View help
```bash
drawing --help
```

### Render ASCII Diagram
```bash
drawing architecture.json -o output/architecture.txt
```

### Render Mermaid Diagram
```bash
drawing architecture.json -f mermaid -o output/architecture.mmd
```

### Render Graphviz Diagram with tree/dot layout
```bash
drawing architecture.json -f graphviz -o output/architecture.dot
```

### Render Graphviz Diagram with neato layout
```bash
drawing architecture-graph.json -f graphviz -l neato -o output/neato.dot
```

### Render Graphviz Diagram with fdp layout
```bash
drawing architecture-graph.json -f graphviz -l fdp -o output/fdp.dot
```
---

## Graphviz commands

### Render SVG as tree/dot layout
```bash
dot -Tsvg output/architecture.dot -o output/architecture.svg
```

### Render PNG as tree/dot layout
```bash
dot -Tpng output/architecture.dot -o output/architecture.png
```

### Render PdF as tree/dot layout
```bash
dot -Tpdf output/architecture.dot -o output/architecture.pdf
```

### Render SVG as neato layout
```bash
neato -Tsvg output/neato.dot -o output/neato.svg
```

### Render PNG as neato layout
```bash
neato -Tpng output/neato.dot -o output/neato.png
```

### Render SVG as fdp layout
```bash
fdp -Tsvg output/fdp.dot -o output/fdp.svg
```

### Render PNG as fdp layout
```bash
fdp -Tpng output/fdp.dot -o output/fdp.png
```

---

## Install Graphviz Package
```bash
apt-get update && apt-get install -y graphviz
```
