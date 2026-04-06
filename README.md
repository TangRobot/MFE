# MFE: Multimodal Hand Exoskeleton

This is the official open-source repository for the paper:

**MFE: A Multimodal Hand Exoskeleton With Interactive Force, Pressure and Thermo-Haptic Feedback**

📄 [Read the Paper](http://arxiv.org/abs/2604.02820)

---

## Hardware

### Hand Exoskeleton (Canonical Version)

#### BOM

| Item | Specification | Quantity | Notes | Link |
|------|---------------|----------|-------|------|
| 3D Printed Parts | See `Hardware/Hand_Exoskeleton_CAD` | 1 set | Print each file once | - |
| Dynamixel Servos | XL-330-M288-T | 5 | with cables & screws | https://en.robotis.com/shop_en/item.php?it_id=902-0163-000 |
| U2D2 Hub | - | 1 | - | https://en.robotis.com/shop_en/item.php?it_id=902-0132-000 |
| U2D2 PHB Set | - | 1 | - | https://en.robotis.com/shop_en/item.php?it_id=902-0145-001 |
| DC Power Supply | 5V | 1 | - | - |
| Screws | M3 × 6 mm | 2 | - | - |
| Screws | M3 × 8 mm | 3 | - | - |
| Screws | M3 × 16 mm | 15 | - | - |
| Lock Nuts | M3 anti-slip | 15 | - | - |
| Heat-set Inserts | M3 × 3 mm (height) × 4.2 mm (OD) | 2 | - | - |
| EVA Foam | 10 cm × 10 cm | 1 | Recommended: 2 mm thickness, Shore hardness 30A | - |
| Velcro Straps (Wide) | 40 cm (length) × 20 mm (width) | 2 | For hand fixation | https://e.tb.cn/h.ih3Ne5haJRBw5nE?tk=OanP5ZXM8IF |
| Velcro Straps (Narrow) | 8 cm (length) × 5 mm (width) | Several | Optional for fingertip fixation | https://e.tb.cn/h.i6odaRXD7jrzqni?tk=6yex5ZX9u82 |

#### 3D Printing Requirements

To print all required parts, you will need:

- 3D printer (0.4 mm nozzle)
- PLA filament (1 spool)
- TPU 95A filament (1 spool)

### Assembly Instructions

0. Before starting the assembly process, configure all Dynamixel servos by assigning their IDs, setting the baud rate, and verifying that each servo operates correctly. Determine the correspondence between each servo and finger in advance.

1. Print all structural components from the directory `Hardware/Hand_Exoskeleton_CAD`, ensuring that you print each file once. For PLA parts, use at least four wall layers and 30% infill, and organize finger linkage components separately to avoid confusion. For TPU 95A parts, use 100% infill, and orient the fingertip sleeves so that the smaller opening faces the print bed.

2. Use a soldering iron to embed two heat-set inserts into the side holes of the lower base component.

3. Assemble the five finger linkages using M3 × 16 mm screws and M3 lock nuts, and adjust the screw tightness so that each joint rotates freely without resistance.

4. Attach the distal ends of each linkage to the servo horns using the longer screws provided in the Dynamixel kit.

5. Mount the servos and corresponding linkages onto the base structure as follows: attach the index and ring fingers to the upper base, attach the middle and little fingers to the lower base, and attach the thumb to the side base. Ensure correct ordering and alignment during installation.

6. Connect the servos in pairs using Dynamixel cables by pairing the index with the ring finger servos and the middle with the little finger servos.

7. Assemble the upper and lower base structures using M3 × 8 mm screws.

8. Attach the side base to the lower base using M3 × 6 mm screws.

9. Connect all servos using Dynamixel cables and link them to the U2D2 Hub.

10. Cut the EVA foam into an appropriate shape and attach it to the surface of the lower base that contacts the back of the hand.

11. Use wide Velcro straps to secure the exoskeleton onto the back of the hand.

12. Use narrow Velcro straps to further secure the fingertip sleeves if necessary.

---

## Software

### Installation

The Dynamixel SDK can be installed using the following command:

```bash
pip install dynamixel_sdk
```

### Usage

Please refer to the [Official Dynamixel SDK Documentation](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/download/) and our [paper](http://arxiv.org/abs/2604.02820) for logic on reading encoder positions and setting force feedback intensity.

A simple implementation example is provided in `Software/MFE_control.py`, which demonstrates force feedback control between the hand exoskeleton and the Inspire RH56BFX robotic hand (both for right hand). Please follow the TODO comments to adapt it to your device, or extend this implementation to develop control logic for other robotic hands.

---

## Citation

If you use this repository in your research, please cite:

```bash
@ARTICLE{Tang2026MFE,
  author={Tang, Ziyuan and Guo, Yitian and Xiao, Chenxi},
  journal={IEEE Robotics and Automation Letters}, 
  title={MFE: A Multimodal Hand Exoskeleton With Interactive Force, Pressure and Thermo-Haptic Feedback}, 
  year={2026},
  volume={11},
  number={3},
  pages={3756-3763},
  doi={10.1109/LRA.2026.3662616}}
```
