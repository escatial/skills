# 3D 批注与分件几何格式

## 消息封装

实际消息中，下面的 JSON 位于 `<annotation>` 和 `</annotation>` 之间。一个块对应一个原模型，可以包含多条批注。其它种类的 `<annotation>` 不属于本协议。

以下路径和数值仅演示格式，操作时使用消息实际提供的值。

```json
{
  "model3dAnnotation": {
    "filePath": "/workspace/assembly.glb",
    "fileName": "assembly.glb",
    "annotations": [
      {
        "annotationId": "note-1",
        "annotation": "把这个分件改成红色",
        "meshName": "Screw",
        "geometry": {
          "type": "file",
          "name": "model-component-gltf%3Anodes%2F3.json",
          "path": "/workspace/annotations/part.json",
          "size": 2048,
          "mimeType": "application/json",
          "format": "model-component-geometry-v1",
          "coordinateSpace": "model"
        }
      }
    ]
  }
}
```

选择批注只发送上述 `<annotation>` 块，通过 geometry.path 引用几何附件，不再额外生成 `<attachment>`。圈画图片及普通附件仍保留原有 attachment 描述。旧消息可能重复描述几何文件，按路径去重，不重复执行批注。

没有单独的 `<attachment>` 不代表几何文件缺失；先读取 geometry.path，再处理附件内的 primitives。应用负责保存文件和维护其会话引用，agent 无需为读取该文件构造额外的附件标记。

| 字段                         | 含义                                                                        |
| ---------------------------- | --------------------------------------------------------------------------- |
| `filePath` / `fileName`      | 原模型的实际路径 / 展示文件名。                                             |
| `annotations[].annotationId` | 批注身份，不是模型对象 ID。                                                 |
| `annotations[].annotation`   | 用户反馈文字；圈画模式可为空。                                              |
| `meshName`                   | 选择模式的兼容展示名，允许为空或重复。                                      |
| `geometry`                   | 可选的完整分件几何文件引用，与 `target` 可以同时存在。                      |
| `geometry.path`              | 实际读取的几何文件路径。应用生成的附件，不是原模型。                        |
| `geometry.name`              | 展示文件名，可含经过 URL 编码的 viewer ID。无需解码它来寻找文件。           |
| `geometry.size` / `mimeType` | 文件字节数 / `application/json`。                                           |
| `geometry.format`            | 当前为 `model-component-geometry-v1`。未知版本不能套用本版假设。            |
| `geometry.coordinateSpace`   | 当前为 `model`，详细坐标约定在文件内部。                                    |
| `target`                     | 可选的 v2 精确引用，见下一节。                                              |
| `visualSelection.screenshot` | 圈画模式图片引用：`type: image`、`path`、`name`、`size` 和可选 `mimeType`。 |

选择与圈画是两种目标：选择包含 `meshName`，圈画包含 `visualSelection`。geometry/target 不与 visualSelection 混用。普通消息没有 `geometry.data`、内嵌 primitives 或截图 dataUrl。

## 可选的 target（version 2）

| 字段                                               | 含义                                                                                                                                                             |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `version`                                          | 固定为 `2`。                                                                                                                                                     |
| `identity.fingerprint`                             | 源文件清单的摘要，算法见后文。                                                                                                                                   |
| `identity.algorithm`                               | `sha256-chunks-v1`；不是单个源文件的完整 SHA-256。                                                                                                               |
| `identity.importProfile`                           | 导入规则版本，按不透明字符串比较；不要写死某个 Three 或加载器版本。                                                                                              |
| `componentId` / `label`                            | 查看器标识 / 展示标签。                                                                                                                                          |
| `source.format`                                    | 来源格式；标识可能使用规整后的格式名，例如 glTF。                                                                                                                |
| `source.occurrencePath`                            | 源对象出现位置的路径段数组；语义依来源格式确定，不是文件系统路径。                                                                                               |
| `source.objectId` / `definitionId` / `primitiveId` | 可选的来源标识；未提供时不补造。                                                                                                                                 |
| `source.stability`                                 | `revision` 或 `native`。即使是 native，也不能证明跨文件版本仍指向同一个对象。                                                                                    |
| `source.derivation`                                | 可选派生信息：`rule: connected-v1`、`sourceId`、`tolerance`、`shellIndices[]`。shellIndices 是连通壳的确定性标签（最小源三角形索引），不是该壳全部三角形的集合。 |
| `granularity`                                      | `component`、`leaf` 或 `material`。                                                                                                                              |
| `scope`                                            | `occurrence` 或 `definition`；definition 范围需要 definitionId。                                                                                                 |
| `anchor.point`                                     | 可选 xyz，位于目标的源局部坐标框架。不要与已烘焙到模型坐标的 geometry.positions 混用。                                                                           |
| `anchor.primitiveId` / `triangleIndex`             | 可选来源 primitive / 三角形索引；不要默认对应导出 JSON 中的 primitive 序号或索引数组位置。                                                                       |
| `anchor.barycentric`                               | 可选重心坐标。仅在确定所指三角形及坐标语义后使用。                                                                                                               |

## 几何附件：model-component-geometry-v1

以下示例只展示一个三角形。sourceFingerprint 示例中的哈希仅用于展示字段类型，不代表实际文件的校验结果。

```json
{
  "format": "model-component-geometry-v1",
  "modelName": "assembly.glb",
  "sourceFingerprint": {
    "algorithm": "sha256-chunks-v1",
    "chunkBytes": 4194304,
    "files": [
      {
        "name": "assembly.glb",
        "size": 1024,
        "sha256Chunks": ["0000000000000000000000000000000000000000000000000000000000000000"]
      }
    ]
  },
  "coordinates": {
    "space": "model",
    "basis": "loader-scene-before-viewer-transforms",
    "upAxisConvention": "y",
    "unit": "m",
    "pose": "authored",
    "description": "Positions already include the model hierarchy and instance transforms."
  },
  "parser": {
    "name": "kimi-model-viewer",
    "threeRevision": "185",
    "format": "glb"
  },
  "component": {
    "name": "Screw",
    "viewerId": "gltf:nodes/3"
  },
  "topology": "positions are flat xyz triples; indices are zero-based triples for triangles or individual indices for points, local to each primitive",
  "primitives": [
    {
      "name": "Screw",
      "mode": "triangles",
      "positions": [10, 0, 0, 11, 0, 0, 10, 1, 0],
      "indices": [0, 1, 2]
    }
  ]
}
```

### 坐标与拓扑

- `coordinates.basis` 表示加载器产出的模型空间，位于查看器旋转、缩放、爆炸等外层变换之前。模型根本身的变换及加载器单位规整已经包含在顶点中；它不保证等于每种原格式的原始数值坐标。
- `upAxisConvention` 是格式上轴约定，不是要求你旋转顶点的指令，也不保证源文件作者遵循该约定。`unit` 可以是 `unknown`、`mm`、`cm`、`m`、`in`、`ft`。
- `pose: authored` 表示导入时的原始姿态。网格已包含该姿态下的骨骼/形变影响，附件不携带可编辑的骨骼、动画轨道、材质或纹理。
- 所选分件可以有多个 primitives，实例的变换已分别应用；无需重新实例化。镜像变换对应的三角形绕序已处理，无需再次翻转。
- `positions.length / 3` 是本 primitive 的存储顶点数。网格三角形数为 `indices.length / 3`；点云的索引数是被引用点的数量。不同 primitive 之间不共享索引空间。
- 原模型会经加载器三角化，所以这里的三角形数可能不同于原 OBJ 多边形面数或 CAD 实体面数。不要把它们的面编号直接互换。
- 保留的顶点可能没有被 indices 引用；材质范围或 source drawRange 会限制索引内容。用于定位的范围、质心等应基于被引用的几何，而不是整个位置缓冲区。
- 数值应有限，positions 长度应为 3 的倍数，indices 应为合法整数且满足 `0 <= index < positions.length / 3`；triangles 的索引数还应为 3 的倍数。未知 mode 或不合法数据应报告，不能默默重解释。

## 源版本核验

两个字段使用同一个算法标签，但存放不同层次的数据：

1. **附件的 `sourceFingerprint` 是分块清单。** `files[0]` 是原始主文件，其后是加载时授权提供的附属文件。对每个文件，从字节零开始按 `chunkBytes` 切块，每块计算 SHA-256，转为小写十六进制，与 sha256Chunks 按顺序比较。最后一块可以较短；零字节文件的块数组为空。同时核对总字节数。校验原始字节，不先规整 OBJ 续行、转码或把 SketchUp 转 GLB。
2. **`target.identity.fingerprint` 是清单的摘要。** 若确需复算，将同一份源文件按每块 4 MiB 的规则得到 chunks，并为每个文件构建字段按此顺序的对象：`{name,size,chunks,primary}`。name 把反斜杠转为 `/`，只有原主文件的 primary 为 true。按主文件优先、其余 name 以 JavaScript 字符串比较排序，保持对象字段顺序，用 JavaScript `JSON.stringify` 的紧凑格式编码为 UTF-8，再求 SHA-256。其它语言实现时必须保持相同的字符串转义与排序语义。

附件文件中 `sourceFingerprint.files[].sha256Chunks` 的单个块摘要不能直接与 `target.identity.fingerprint` 比较。完整引用恢复还要求 `algorithm` 和 `importProfile` 一致；没有当前导入器的 profile 时，不声称已完成这项一致性验证。

文件名只是解析来源的线索。主文件由消息 filePath 指定；附属文件路径需结合实际资源布局确定，不要把附件目录误当作原模型资源目录，也不要以同名文件替代无法确认的依赖。

源版本不匹配时，几何附件仍可用于描述用户当时选择的形状和位置，但不足以证明它对应当前原文件中的哪个可编辑对象。完整几何相同且完全重叠的对象也可能无法仅靠坐标区分。
