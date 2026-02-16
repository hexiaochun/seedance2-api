# 国风水墨打斗 - Seedance 2.0 案例

## 概述

使用 Seedance 2.0 生成的 15 秒国风水墨武侠打斗视频。

| 项目 | 详情 |
|------|------|
| 风格 | 中国水墨武侠风 |
| 时长 | 15 秒 |
| 比例 | 9:16 竖屏 |
| 角色 | 白衣长枪侠客 vs 红衣双刀女侠 |
| 场景 | 深秋枫叶林 |
| 功能模式 | omni_reference（全能模式） |
| 速度模式 | seedance_2.0_fast |
| 总耗积分 | 约 195（图片 15×3 + 视频 150） |

## 资产清单

### 输入素材（Seedream 4.5 生成）

| 文件 | 说明 | 用途 |
|------|------|------|
| `images/01-spear-warrior.png` | 白衣长枪侠客 | @image_file_1 角色形象 |
| `images/02-dual-swords-warrior.png` | 红衣双刀女侠 | @image_file_2 角色形象 |
| `images/03-maple-forest.png` | 深秋枫叶林场景 | @image_file_3 场景参考 |

### 输出视频

| 文件 | 说明 |
|------|------|
| `video/guofeng-fight-output.mp4` | 最终生成的 15 秒打斗视频 |

## 分镜提示词

```
中国水墨武侠风格，15秒，9:16竖屏，枫叶飘落的深秋意境

0-2秒：远景，@image_file_3 枫叶林深处，薄雾笼罩，红叶纷飞，镜头缓缓推近，隐约可见两道身影对峙
2-4秒：中景，@image_file_1 白衣长枪侠客 与 @image_file_2 红衣双刀女侠 对峙而立，秋风卷起落叶，杀气渐浓
4-6秒：快速推近特写，两人眼神对视，瞳孔中映出对方身影，墨水飞溅特效
6-9秒：中景快速镜头，长枪突刺如龙，双刀旋转格挡，兵器碰撞瞬间墨水四溅，水墨笔触特效跟随武器轨迹
9-12秒：环绕镜头，激烈交锋，长枪横扫，双刀翻飞，枫叶被内力气浪卷起漫天飞舞，水墨晕染效果
12-14秒：慢动作，双方同时跃起，在空中交锋一击，兵器碰撞产生巨大的墨水爆裂特效
14-15秒：定格，两人背对背落地，枫叶缓缓飘落，画面渐变为纯水墨留白

【声音】古风激昂配乐 + 金属碰撞音效 + 风声落叶声
【参考】@image_file_1 长枪侠客形象，@image_file_2 双刀女侠形象，@image_file_3 枫叶林场景
```

> **注意：** 也兼容旧版引用语法（@图片1、@图片2、@图片3）

## Seedream 4.5 图片提示词

### @image_file_1 长枪侠客

```
Chinese ink wash painting style, a male martial arts warrior standing in a heroic pose
holding a long spear, wearing flowing white and silver traditional hanfu robes, hair tied
in a topknot with a silver crown, stoic expression, slender athletic build, ink splash
effects around the spear tip, traditional Chinese calligraphy brush stroke aesthetic,
misty atmosphere, full body shot, portrait orientation, high quality, detailed, elegant
sumi-e art style
```

### @image_file_2 双刀女侠

```
Chinese ink wash painting style, a fierce female warrior in a dynamic stance wielding
dual dao swords, wearing dark red and black traditional Chinese martial arts attire with
flowing ribbons, long black hair partially tied up with a jade hairpin, fierce determined
expression, ink splash effects trailing from the blades, traditional Chinese calligraphy
brush stroke aesthetic, misty atmosphere, full body shot, portrait orientation, high
quality, detailed, elegant sumi-e art style
```

### @image_file_3 枫叶林场景

```
Chinese ink wash painting style, a serene ancient maple forest in deep autumn, vibrant
red and golden maple leaves covering the trees and ground, a narrow stone path winding
through the forest, misty atmosphere with sunlight filtering through the canopy creating
god rays, ink wash texture blending with the natural scenery, some leaves gently falling,
traditional Chinese landscape painting aesthetic, cinematic composition, portrait
orientation, high quality, detailed, sumi-e meets reality
```

## API 调用参数

### Seedance 2.0 视频生成

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "（见上方分镜提示词）",
    "functionMode": "omni_reference",
    "image_files": [
      "images/01-spear-warrior.png 的 URL",
      "images/02-dual-swords-warrior.png 的 URL",
      "images/03-maple-forest.png 的 URL"
    ],
    "ratio": "9:16",
    "duration": 15,
    "model": "seedance_2.0_fast"
  }
}
```

## 复现步骤

1. 使用 Seedream 4.5（`fal-ai/bytedance/seedream/v4.5/text-to-image`）生成 3 张参考图，`image_size: portrait_16_9`
2. 将参考图 URL 按顺序放入 `image_files` 数组
3. 使用上方分镜提示词提交 Seedance 2.0（`st-ai/super-seed2`）任务，`functionMode: "omni_reference"`
4. 等待约 5-10 分钟获取视频结果
