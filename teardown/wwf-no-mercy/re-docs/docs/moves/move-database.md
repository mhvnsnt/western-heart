# Move Database

## Overview

This is the human-readable master reference for all moves available in VPG Engine. Moves are organized by the slot categories they are eligible for, matching how the original game presents them in create-a-wrestler mode.

A move may appear in multiple slot category tables — this means it is eligible for assignment to any of those slot categories in a character's `moves.json`.

For power tier definitions, boolean flag descriptions, and feature values, see `data/README.md`.

> **Status**: This file is the authoritative human-readable reference. The programmatic version is `move-database.json`, currently in progress.

---

## Slot Categories

- [Front Weak Grapple Slots 1–4](#front-weak-grapple-slots-1-4)
- [Front Weak Grapple Slots 5–8](#front-weak-grapple-slots-5-8)
- [Front Strong Grapple Slots 1–8](#front-strong-grapple-slots-1-8)
- [Front Finisher Slot](#front-finisher-slot)

> Additional slot categories (Back Grapple, Ground, Turnbuckle, Ringside, Apron, Irish Whip, Taunt, Double-Team) to be documented.

---

### Front Weak Grapple 1-4

| Move                  | Power | KO    | Bleed | Feature |
| --------------------- | ----- | ----- | ----- | ------- |
| Arm Drag              | F     | FALSE | FALSE |         |
| Chop 01               | F     | FALSE | FALSE |         |
| Chop 02               | F     | FALSE | FALSE |         |
| Chop 03               | F     | FALSE | TRUE  |         |
| Chop 04               | F     | FALSE | FALSE |         |
| Club to Neck          | F     | FALSE | FALSE |         |
| Double Axe Handle     | F     | FALSE | FALSE |         |
| Double Leg Takedown   | F     | FALSE | FALSE |         |
| Elbow Strike          | F     | FALSE | FALSE |         |
| Elbow to Back of Head | F     | FALSE | FALSE |         |
| European Uppercut     | F     | FALSE | FALSE |         |
| Eye Rake              | F     | FALSE | FALSE |         |
| Fireman Carry         | F     | FALSE | FALSE |         |
| Head Butt 01          | F     | FALSE | TRUE  |         |
| Head Butt 02          | F     | FALSE | TRUE  |         |
| Head Butt 03          | F     | FALSE | TRUE  |         |
| Headlock and Punch    | F     | FALSE | FALSE |         |
| Headlock and Thrust   | F     | FALSE | FALSE |         |
| Jumping Front Kick    | F     | FALSE | FALSE |         |
| Knee Lift             | F     | FALSE | FALSE |         |
| Knee Strike           | F     | FALSE | FALSE |         |
| Knee Sweep            | F     | FALSE | FALSE |         |
| Mini Shin Kicks       | F     | FALSE | FALSE |         |
| Overhand Punch        | F     | FALSE | FALSE |         |
| One Hand Scoop Slam   | F     | FALSE | FALSE |         |
| Scoop Slam            | E     | FALSE | FALSE |         |
| Slap                  | F     | FALSE | FALSE |         |
| Snapmare              | F     | FALSE | FALSE |         |
| Throat Thrust         | F     | FALSE | FALSE |         |
| Underhand Hook Punch  | F     | FALSE | FALSE |         |

### Front Weak Grapple 5-8

| Move                                       | Power | KO    | Bleed | Feature |
|--------------------------------------------|-------|-------|-------|---------|
| Arm Dragon Screw                           | F     | FALSE | FALSE | null    |
| Arm Wrench / Elbow Smash                   | E     | FALSE | FALSE | null    |
| Arm Wrench with Hook Kick                  | E     | FALSE | FALSE | null    |
| Back Body Flip                             | E     | FALSE | FALSE | null    |
| Chop Down                                  | E     | FALSE | FALSE | null    |
| Drop Suplex 01                             | E     | FALSE | FALSE | null    |
| Drop Suplex 02                             | E     | FALSE | FALSE | null    |
| Double Underhook Suplex                    | E     | FALSE | FALSE | null    |
| Fallaway Slam                              | E     | FALSE | FALSE | null    |
| Falling Neck Breaker                       | E     | FALSE | FALSE | null    |
| Falling Powerslam                          | E     | FALSE | FALSE | null    |
| Falling Suplex                             | D     | FALSE | FALSE | null    |
| Gordbuster 01                              | E     | FALSE | FALSE | null    |
| Gordbuster 02                              | D     | FALSE | FALSE | null    |
| Headlock Takedown                          | E     | FALSE | FALSE | null    |
| Head Scissor Takedown 01                   | E     | FALSE | FALSE | null    |
| Head Scissor Takedown 02                   | E     | FALSE | FALSE | null    |
| Hip Throw                                  | E     | FALSE | FALSE | null    |
| Hip Toss                                   | E     | FALSE | FALSE | null    |
| Jawbreaker                                 | F     | FALSE | FALSE | null    |
| Knee Strikes 01                            | F     | FALSE | FALSE | null    |
| Knee Strikes 02                            | F     | FALSE | FALSE | null    |
| Knee Strikes 03                            | E     | FALSE | FALSE | null    |
| Mini Chops                                 | E     | FALSE | FALSE | null    |
| Neck Breaker 01                            | E     | FALSE | FALSE | null    |
| Neck Breaker 02                            | E     | FALSE | FALSE | null    |
| Piledriver 01                              | D     | FALSE | FALSE | null    |
| Piledriver 02                              | E     | FALSE | FALSE | null    |
| Piledriver 03                              | D     | FALSE | FALSE | null    |
| Piledriver 04                              | D     | FALSE | FALSE | null    |
| Rib Breaker                                | E     | FALSE | FALSE | null    |
| Russian Leg Sweep                          | E     | FALSE | FALSE | null    |
| Shoulder Breaker                           | E     | FALSE | FALSE | null    |
| Shoulder Thrusts                           | E     | FALSE | FALSE | null    |
| Snap Suplex                                | E     | FALSE | FALSE | null    |
| Stall Suplex                               | E     | FALSE | FALSE | null    |
| Suplex                                     | E     | FALSE | FALSE | null    |
| Tie Up Knee Strikes                        | F     | FALSE | FALSE | null    |
| Underhook Suplex / Knee                    | D     | FALSE | FALSE | null    |


### Front Strong Grapple 1-8

| Move                                       | Power | KO    | Bleed | Feature |
|--------------------------------------------|-------|-------|-------|---------|
| Bearhug                                    | E     | FALSE | FALSE | Submit  |
| Backslide Pin                              | C     | FALSE | FALSE | Pin     |
| Belly to Back Flip Suplex                  | C     | TRUE  | FALSE | null    |
| Belly to Back Spin Suplex                  | C     | FALSE | FALSE | null    |
| Belly to Back Suplex                       | C     | FALSE | FALSE | null    |
| Belly to Belly Suplex 01                   | C     | FALSE | FALSE | null    |
| Belly to Belly Suplex 02                   | C     | FALSE | FALSE | null    |
| Body Press Drop                            | D     | FALSE | FALSE | null    |
| Body Press to Front Slam                   | C     | FALSE | FALSE | null    |
| Brainbuster                                | B     | FALSE | FALSE | null    |
| Canadian Back Breaker                      | E     | FALSE | FALSE | Submit  |
| Capture Suplex                             | B     | TRUE  | FALSE | null    |
| Chicken Wing Suplex Pin                    | C     | FALSE | FALSE | null    |
| Chokeslam from Hell                        | C     | FALSE | FALSE | null    |
| Chokeslam 01                               | C     | FALSE | FALSE | null    |
| Chokeslam 02                               | C     | TRUE  | FALSE | null    |
| Choke Takedown                             | D     | FALSE | FALSE | null    |
| Climb Up Wheel Kick                        | D     | FALSE | FALSE | null    |
| Clinching Slam                             | C     | FALSE | FALSE | null    |
| DDT 01                                     | C     | FALSE | FALSE | null    |
| DDT 02                                     | C     | FALSE | TRUE  | null    |
| DDT 03                                     | D     | FALSE | FALSE | null    |
| Death Valley Driver                        | C     | TRUE  | FALSE | null    |
| Double Arm DDT                             | C     | FALSE | TRUE  | null    |
| Double Chokelift Slam                      | C     | FALSE | FALSE | null    |
| Dragon Screw 01                            | E     | FALSE | FALSE | null    |
| Dragon Screw 02                            | E     | FALSE | FALSE | null    |
| Falcon Arrow                               | C     | FALSE | FALSE | null    |
| Fallaway Slam                              | D     | FALSE | FALSE | null    |
| Falling Hip Toss                           | C     | FALSE | FALSE | null    |
| Falling Nexk Breaker                       | D     | FALSE | FALSE | null    |
| Fireman Carry to Pancake                   | D     | FALSE | FALSE | null    |
| Fire Thunder Driver                        | C     | TRUE  | TRUE  | null    |
| Fisherman DDT                              | C     | FALSE | FALSE | null    |
| Fisherman Suplex                           | C     | FALSE | FALSE | null    |
| Front Face Pancake                         | C     | FALSE | FALSE | null    |
| Front Powerslam                            | E     | FALSE | FALSE | null    |
| Giant Headbutt                             | C     | FALSE | TRUE  | null    |
| Guillotine Choke                           | F     | FALSE | FALSE | null    |
| Headlock                                   | F     | FALSE | FALSE | null    |
| Hopping Rolling Pin                        | C     | FALSE | FALSE | null    |
| Hopping Sunset Flip Pin                    | C     | FALSE | FALSE | null    |
| Hurracanrana Pin                           | D     | FALSE | FALSE | null    |
| Judo Front Slam                            | E     | FALSE | FALSE | null    |
| Knee Smash                                 | C     | FALSE | FALSE | null    |
| Manhattan Drop                             | D     | FALSE | FALSE | null    |
| Michinoku Driver                           | C     | FALSE | FALSE | null    |
| Military Press                             | E     | FALSE | FALSE | null    |
| Northern Lights Suplex 01                  | C     | FALSE | FALSE | null    |
| Northern Lights Suplex 02                  | E     | FALSE | FALSE | null    |
| Oklahoma Slam                              | B     | FALSE | FALSE | null    |
| Powerbomp Pin 01                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 02                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 03                           | B     | FALSE | FALSE | null    |
| Powerbomp Pin 04                           | B     | FALSE | FALSE | null    |
| Powerbomp Pin 05                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 06                           | B     | FALSE | FALSE | null    |
| Powerbomp Pin 07                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 08                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 09                           | C     | FALSE | FALSE | null    |
| Powerslam                                  | D     | FALSE | FALSE | null    |
| Reverse Armbar                             | F     | FALSE | FALSE | null    |
| Reverse Suplex                             | D     | FALSE | FALSE | null    |
| Rolling Leg Lock                           | F     | FALSE | FALSE | null    |
| Rope Drop Clothesline                      | E     | FALSE | FALSE | null    |
| Running Knee Strike                        | E     | FALSE | FALSE | null    |
| Running Powerbomb Pin                      | C     | FALSE | FALSE | null    |
| Sambo Suplex                               | C     | FALSE | FALSE | null    |
| Scoop Piledriver                           | D     | FALSE | FALSE | null    |
| Shoulder Breaker Thrust                    | E     | FALSE | FALSE | null    |
| Sidewalk Slam                              | D     | FALSE | FALSE | null    |
| Small Package                              | C     | FALSE | FALSE | null    |
| Snap Powerbomb 01                          | C     | FALSE | FALSE | null    |
| Snap Powerbomb 02                          | C     | TRUE  | FALSE | null    |
| Snap Powerbomb 03                          | C     | FALSE | FALSE | null    |
| Somersault Kick                            | F     | FALSE | FALSE | null    |
| Spinning Leg Takedown                      | C     | FALSE | FALSE | null    |
| Standing Armbar                            | F     | FALSE | FALSE | Submit  |
| Standing Clothesline                       | D     | FALSE | FALSE | null    |
| Stalling Brainbuster                       | B     | FALSE | FALSE | null    |
| Stalling Piledriver                        | C     | FALSE | FALSE | null    |
| Strong Sambo Suplex                        | C     | TRUE  | FALSE | null    |
| Super Shoulder Breaker                     | B     | FALSE | FALSE | null    |
| Sweep with Mounted Punching                | F     | FALSE | FALSE | Submit  |
| Tiger Driver                               | D     | FALSE | FALSE | null    |
| Tiger Driver with Pin                      | C     | FALSE | FALSE | Pin     |
| Tilt A Whirl Piledriver                    | D     | FALSE | FALSE | null    |
| Trapping Headbutts                         | E     | FALSE | TRUE  | null    |
| Triple Powerbomb Pin                       | C     | FALSE | FALSE | Pin     |
| Two Handed Choke Lift                      | E     | FALSE | FALSE | Submit  |
| T-Bone Suplex 01                           | D     | FALSE | FALSE | null    |
| T-Bone Suplex 02                           | C     | FALSE | FALSE | null    |
| Underhook Back Breaker                     | C     | FALSE | FALSE | null    |
| Underhook Belly to Belly Suplex 01         | C     | FALSE | FALSE | null    |
| Underhook Belly to Belly Suplex 02         | C     | TRUE  | FALSE | null    |
| Arm Dragon Screw                           | F     | FALSE | FALSE | null    |
| Arm Wrench / Elbow Smash                   | E     | FALSE | FALSE | null    |
| Arm Wrench with Hook Kick                  | E     | FALSE | FALSE | null    |
| Back Body Flip                             | E     | FALSE | FALSE | null    |
| Chop Down                                  | E     | FALSE | FALSE | null    |
| Drop Suplex 01                             | E     | FALSE | FALSE | null    |
| Drop Suplex 02                             | E     | FALSE | FALSE | null    |
| Double Underhook Suplex                    | E     | FALSE | FALSE | null    |
| Fallaway Slam                              | E     | FALSE | FALSE | null    |
| Falling Neck Breaker                       | E     | FALSE | FALSE | null    |
| Falling Powerslam                          | E     | FALSE | FALSE | null    |
| Falling Suplex                             | D     | FALSE | FALSE | null    |
| Gordbuster 01                              | E     | FALSE | FALSE | null    |
| Gordbuster 02                              | D     | FALSE | FALSE | null    |
| Headlock Takedown                          | E     | FALSE | FALSE | null    |
| Head Scissor Takedown 01                   | E     | FALSE | FALSE | null    |
| Head Scissor Takedown 02                   | E     | FALSE | FALSE | null    |
| Hip Throw                                  | E     | FALSE | FALSE | null    |
| Hip Toss                                   | E     | FALSE | FALSE | null    |
| Jawbreaker                                 | F     | FALSE | FALSE | null    |
| Knee Strikes 01                            | F     | FALSE | FALSE | null    |
| Knee Strikes 02                            | F     | FALSE | FALSE | null    |
| Knee Strikes 03                            | E     | FALSE | FALSE | null    |
| Mini Chops                                 | E     | FALSE | FALSE | null    |
| Neck Breaker 01                            | E     | FALSE | FALSE | null    |
| Neck Breaker 02                            | E     | FALSE | FALSE | null    |
| Piledriver 01                              | D     | FALSE | FALSE | null    |
| Piledriver 02                              | E     | FALSE | FALSE | null    |
| Piledriver 03                              | D     | FALSE | FALSE | null    |
| Piledriver 04                              | D     | FALSE | FALSE | null    |
| Rib Breaker                                | E     | FALSE | FALSE | null    |
| Russian Leg Sweep                          | E     | FALSE | FALSE | null    |
| Shoulder Breaker                           | E     | FALSE | FALSE | null    |
| Shoulder Thrusts                           | E     | FALSE | FALSE | null    |
| Snap Suplex                                | E     | FALSE | FALSE | null    |
| Stall Suplex                               | E     | FALSE | FALSE | null    |
| Suplex                                     | E     | FALSE | FALSE | null    |
| Tie Up Knee Strikes                        | F     | FALSE | FALSE | null    |
| Underhook Suplex / Knee                    | D     | FALSE | FALSE | null    |


### Front Finisher

| Move                                       | Power | KO    | Bleed | Feature |
|--------------------------------------------|-------|-------|-------|---------|
| Big Swing                                  | F     | FALSE | FALSE | Null    |
| Brainbuster DDT                            | S     | TRUE  | FALSE | Null    |
| Burning Combo                              | S     | TRUE  | FALSE | Null    |
| Butterfly Lock                             | F     | FALSE | FALSE | Submit  |
| Censor Kick                                | B     | TRUE  | FALSE | Null    |
| Chicken Wing Jawbreaker                    | B     | TRUE  | FALSE | Null    |
| Continuous Powerbomb / Death Valley Driver | S     | FALSE | FALSE | Null    |
| Cradle DDT                                 | C     | TRUE  | FALSE | Null    |
| Cross DDT                                  | A     | TRUE  | FALSE | Null    |
| Cross Heel Hold                            | E     | FALSE | FALSE | Submit  |
| Dominator                                  | S     | TRUE  | FALSE | Null    |
| Double Dragon Screw 01                     | A     | FALSE | FALSE | Null    |
| Double Dragon Screw 02                     | A     | FALSE | FALSE | Null    |
| Downward Spiral                            | S     | TRUE  | TRUE  | Null    |
| Emerald Fusion                             | S     | TRUE  | FALSE | Null    |
| FameAsser                                  | S     | TRUE  | TRUE  | Null    |
| Figure Four Combo Pin                      | D     | FALSE | FALSE | Pin     |
| Fireball                                   | A     | TRUE  | FALSE | Null    |
| Fire Thunder                               | S     | TRUE  | FALSE | Null    |
| Flipping Armbar                            | F     | FALSE | FALSE | Submit  |
| Flowing DDT                                | A     | TRUE  | FALSE | Null    |
| Front Russian Sweep                        | S     | TRUE  | TRUE  | Null    |
| Hangmans DDT                               | S     | TRUE  | FALSE | Null    |
| Helicopter Pin                             | S     | FALSE | FALSE | Pin     |
| Hip Toss to Submission                     | G     | FALSE | FALSE | Submit  |
| Huge Chokeslam                             | S     | TRUE  | FALSE | Null    |
| Insider Edge                               | S     | TRUE  | FALSE | Null    |
| Inverted DDT                               | B     | TRUE  | FALSE | Null    |
| Iron Claw                                  | A     | FALSE | TRUE  | Submit  |
| Jack Hammer                                | S     | FALSE | FALSE | Pin     |
| Jackknife Powerbomb                        | S     | TRUE  | FALSE | Null    |
| Jericho Powerbomb                          | A     | TRUE  | FALSE | Null    |
| Jump Swinging DDT                          | S     | TRUE  | FALSE | Null    |
| Kicking Combination 01                     | B     | TRUE  | FALSE | Null    |
| Kicking Combination 02                     | S     | TRUE  | FALSE | Null    |
| Kohya-Otoshi                               | S     | FALSE | FALSE | Pin     |
| Last Ride                                  | S     | TRUE  | FALSE | Null    |
| Leg Sweep / Strong Punching                | F     | FALSE | FALSE | Submit  |
| Linda Slap                                 | B     | TRUE  | FALSE | Null    |
| Mac Stunner                                | S     | TRUE  | FALSE | Null    |
| Mandible Claw                              | E     | FALSE | FALSE | Submit  |
| Mu-ken                                     | A     | FALSE | FALSE | Pin     |
| Old Man Flop                               | G     | FALSE | FALSE | Null    |
| Olympic Slam                               | A     | TRUE  | FALSE | Null    |
| Orange Crush Pin                           | S     | FALSE | FALSE | Pin     |
| Pedigree                                   | S     | TRUE  | TRUE  | Null    |
| Poison Mist                                | D     | FALSE | FALSE | Null    |
| Powerbomb Pin with Slide                   | S     | FALSE | FALSE | Pin     |
| Powerbomb to Facebuster                    | S     | TRUE  | FALSE | Null    |
| Power Clothesline                          | S     | TRUE  | FALSE | Null    |
| Punching Combination 01                    | F     | FALSE | FALSE | Null    |
| Punching Combination 02                    | F     | FALSE | FALSE | Null    |
| Punching Combination 03                    | A     | TRUE  | TRUE  | Null    |
| Rikishi Driver                             | S     | TRUE  | TRUE  | Null    |
| Rios Driver                                | A     | TRUE  | TRUE  | Null    |
| Rockbottom                                 | A     | TRUE  | FALSE | Null    |
| Rushing Armbar                             | E     | FALSE | FALSE | Submit  |
| Russian Neck Drop                          | S     | TRUE  | FALSE | Null    |
| Scoop Reverse DDT                          | B     | TRUE  | FALSE | Null    |
| Screwdriver                                | S     | TRUE  | TRUE  | Null    |
| Shake Rattle and Roll                      | S     | TRUE  | TRUE  | Null    |
| Sidewalk Slam with Submission              | G     | FALSE | FALSE | Null    |
| Six Seconds Magic                          | F     | FALSE | FALSE | Submit  |
| Sky High                                   | S     | FALSE | FALSE | Pin     |
| Small Package DDT                          | S     | TRUE  | FALSE | Null    |
| Snowplow                                   | A     | TRUE  | FALSE | Null    |
| Spinning Falcon Arrow                      | S     | FALSE | FALSE | Pin     |
| Spiral Bomb                                | S     | FALSE | FALSE | Pin     |
| Stephanie Slap                             | B     | TRUE  | FALSE | Null    |
| STO 01                                     | S     | TRUE  | FALSE | Null    |
| STO 02                                     | B     | FALSE | FALSE | Null    |
| Stone Cold Stunner                         | S     | TRUE  | FALSE | Null    |
| Striking Combination                       | A     | TRUE  | FALSE | Null    |
| Strong Lariat                              | S     | TRUE  | FALSE | Null    |
| Sumo Attack 01                             | C     | TRUE  | FALSE | Null    |
| Sumo Attack 02                             | B     | FALSE | FALSE | Null    |
| Super Knee Strike                          | A     | TRUE  | FALSE | Null    |
| Super Powerbomb Pin 01                     | A     | FALSE | FALSE | Pin     |
| Super Powerbomb Pin 02                     | S     | FALSE | FALSE | Pin     |
| Super Snap Powerbomb 01                    | S     | TRUE  | FALSE | Null    |
| Super Snap Powerbomb 02                    | S     | TRUE  | FALSE | Null    |
| Sweet Chin Music                           | A     | TRUE  | FALSE | Null    |
| Tazzplex                                   | S     | TRUE  | FALSE | Null    |
| The Morality Check                         | D     | FALSE | FALSE | Null    |
| Tiger Driver                               | S     | FALSE | FALSE | Pin     |
| TKO                                        | S     | TRUE  | FALSE | Null    |
| Tombstone Piledriver                       | S     | TRUE  | TRUE  | Null    |
| Twist of Fate                              | A     | TRUE  | FALSE | Null    |
| Two Handed Chokeslam                       | S     | TRUE  | FALSE | Null    |
| Ultimate Armbar                            | F     | FALSE | FALSE | Submit  |
| X-Factor                                   | S     | TRUE  | TRUE  | Null    |
| 3/4 Turn Neck Breaker                      | S     | TRUE  | FALSE | Null    |
| Bearhug                                    | E     | FALSE | FALSE | Submit  |
| Backslide Pin                              | C     | FALSE | FALSE | Pin     |
| Belly to Back Flip Suplex                  | C     | TRUE  | FALSE | null    |
| Belly to Back Spin Suplex                  | C     | FALSE | FALSE | null    |
| Belly to Back Suplex                       | C     | FALSE | FALSE | null    |
| Belly to Belly Suplex 01                   | C     | FALSE | FALSE | null    |
| Belly to Belly Suplex 02                   | C     | FALSE | FALSE | null    |
| Body Press Drop                            | D     | FALSE | FALSE | null    |
| Body Press to Front Slam                   | C     | FALSE | FALSE | null    |
| Brainbuster                                | B     | FALSE | FALSE | null    |
| Canadian Back Breaker                      | E     | FALSE | FALSE | Submit  |
| Capture Suplex                             | B     | TRUE  | FALSE | null    |
| Chicken Wing Suplex Pin                    | C     | FALSE | FALSE | null    |
| Chokeslam from Hell                        | C     | FALSE | FALSE | null    |
| Chokeslam 01                               | C     | FALSE | FALSE | null    |
| Chokeslam 02                               | C     | TRUE  | FALSE | null    |
| Choke Takedown                             | D     | FALSE | FALSE | null    |
| Climb Up Wheel Kick                        | D     | FALSE | FALSE | null    |
| Clinching Slam                             | C     | FALSE | FALSE | null    |
| DDT 01                                     | C     | FALSE | FALSE | null    |
| DDT 02                                     | C     | FALSE | TRUE  | null    |
| DDT 03                                     | D     | FALSE | FALSE | null    |
| Death Valley Driver                        | C     | TRUE  | FALSE | null    |
| Double Arm DDT                             | C     | FALSE | TRUE  | null    |
| Double Chokelift Slam                      | C     | FALSE | FALSE | null    |
| Dragon Screw 01                            | E     | FALSE | FALSE | null    |
| Dragon Screw 02                            | E     | FALSE | FALSE | null    |
| Falcon Arrow                               | C     | FALSE | FALSE | null    |
| Fallaway Slam                              | D     | FALSE | FALSE | null    |
| Falling Hip Toss                           | C     | FALSE | FALSE | null    |
| Falling Nexk Breaker                       | D     | FALSE | FALSE | null    |
| Fireman Carry to Pancake                   | D     | FALSE | FALSE | null    |
| Fire Thunder Driver                        | C     | TRUE  | TRUE  | null    |
| Fisherman DDT                              | C     | FALSE | FALSE | null    |
| Fisherman Suplex                           | C     | FALSE | FALSE | null    |
| Front Face Pancake                         | C     | FALSE | FALSE | null    |
| Front Powerslam                            | E     | FALSE | FALSE | null    |
| Giant Headbutt                             | C     | FALSE | TRUE  | null    |
| Guillotine Choke                           | F     | FALSE | FALSE | null    |
| Headlock                                   | F     | FALSE | FALSE | null    |
| Hopping Rolling Pin                        | C     | FALSE | FALSE | null    |
| Hopping Sunset Flip Pin                    | C     | FALSE | FALSE | null    |
| Hurracanrana Pin                           | D     | FALSE | FALSE | null    |
| Judo Front Slam                            | E     | FALSE | FALSE | null    |
| Knee Smash                                 | C     | FALSE | FALSE | null    |
| Manhattan Drop                             | D     | FALSE | FALSE | null    |
| Michinoku Driver                           | C     | FALSE | FALSE | null    |
| Military Press                             | E     | FALSE | FALSE | null    |
| Northern Lights Suplex 01                  | C     | FALSE | FALSE | null    |
| Northern Lights Suplex 02                  | E     | FALSE | FALSE | null    |
| Oklahoma Slam                              | B     | FALSE | FALSE | null    |
| Powerbomp Pin 01                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 02                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 03                           | B     | FALSE | FALSE | null    |
| Powerbomp Pin 04                           | B     | FALSE | FALSE | null    |
| Powerbomp Pin 05                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 06                           | B     | FALSE | FALSE | null    |
| Powerbomp Pin 07                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 08                           | C     | FALSE | FALSE | null    |
| Powerbomp Pin 09                           | C     | FALSE | FALSE | null    |
| Powerslam                                  | D     | FALSE | FALSE | null    |
| Reverse Armbar                             | F     | FALSE | FALSE | null    |
| Reverse Suplex                             | D     | FALSE | FALSE | null    |
| Rolling Leg Lock                           | F     | FALSE | FALSE | null    |
| Rope Drop Clothesline                      | E     | FALSE | FALSE | null    |
| Running Knee Strike                        | E     | FALSE | FALSE | null    |
| Running Powerbomb Pin                      | C     | FALSE | FALSE | null    |
| Sambo Suplex                               | C     | FALSE | FALSE | null    |
| Scoop Piledriver                           | D     | FALSE | FALSE | null    |
| Shoulder Breaker Thrust                    | E     | FALSE | FALSE | null    |
| Sidewalk Slam                              | D     | FALSE | FALSE | null    |
| Small Package                              | C     | FALSE | FALSE | null    |
| Snap Powerbomb 01                          | C     | FALSE | FALSE | null    |
| Snap Powerbomb 02                          | C     | TRUE  | FALSE | null    |
| Snap Powerbomb 03                          | C     | FALSE | FALSE | null    |
| Somersault Kick                            | F     | FALSE | FALSE | null    |
| Spinning Leg Takedown                      | C     | FALSE | FALSE | null    |
| Standing Armbar                            | F     | FALSE | FALSE | Submit  |
| Standing Clothesline                       | D     | FALSE | FALSE | null    |
| Stalling Brainbuster                       | B     | FALSE | FALSE | null    |
| Stalling Piledriver                        | C     | FALSE | FALSE | null    |
| Strong Sambo Suplex                        | C     | TRUE  | FALSE | null    |
| Super Shoulder Breaker                     | B     | FALSE | FALSE | null    |
| Sweep with Mounted Punching                | F     | FALSE | FALSE | Submit  |
| Tiger Driver                               | D     | FALSE | FALSE | null    |
| Tiger Driver with Pin                      | C     | FALSE | FALSE | Pin     |
| Tilt A Whirl Piledriver                    | D     | FALSE | FALSE | null    |
| Trapping Headbutts                         | E     | FALSE | TRUE  | null    |
| Triple Powerbomb Pin                       | C     | FALSE | FALSE | Pin     |
| Two Handed Choke Lift                      | E     | FALSE | FALSE | Submit  |
| T-Bone Suplex 01                           | D     | FALSE | FALSE | null    |
| T-Bone Suplex 02                           | C     | FALSE | FALSE | null    |
| Underhook Back Breaker                     | C     | FALSE | FALSE | null    |
| Underhook Belly to Belly Suplex 01         | C     | FALSE | FALSE | null    |
| Underhook Belly to Belly Suplex 02         | C     | TRUE  | FALSE | null    |
| Arm Dragon Screw                           | F     | FALSE | FALSE | null    |
| Arm Wrench / Elbow Smash                   | E     | FALSE | FALSE | null    |
| Arm Wrench with Hook Kick                  | E     | FALSE | FALSE | null    |
| Back Body Flip                             | E     | FALSE | FALSE | null    |
| Chop Down                                  | E     | FALSE | FALSE | null    |
| Drop Suplex 01                             | E     | FALSE | FALSE | null    |
| Drop Suplex 02                             | E     | FALSE | FALSE | null    |
| Double Underhook Suplex                    | E     | FALSE | FALSE | null    |
| Fallaway Slam                              | E     | FALSE | FALSE | null    |
| Falling Neck Breaker                       | E     | FALSE | FALSE | null    |
| Falling Powerslam                          | E     | FALSE | FALSE | null    |
| Falling Suplex                             | D     | FALSE | FALSE | null    |
| Gordbuster 01                              | E     | FALSE | FALSE | null    |
| Gordbuster 02                              | D     | FALSE | FALSE | null    |
| Headlock Takedown                          | E     | FALSE | FALSE | null    |
| Head Scissor Takedown 01                   | E     | FALSE | FALSE | null    |
| Head Scissor Takedown 02                   | E     | FALSE | FALSE | null    |
| Hip Throw                                  | E     | FALSE | FALSE | null    |
| Hip Toss                                   | E     | FALSE | FALSE | null    |
| Jawbreaker                                 | F     | FALSE | FALSE | null    |
| Knee Strikes 01                            | F     | FALSE | FALSE | null    |
| Knee Strikes 02                            | F     | FALSE | FALSE | null    |
| Knee Strikes 03                            | E     | FALSE | FALSE | null    |
| Mini Chops                                 | E     | FALSE | FALSE | null    |
| Neck Breaker 01                            | E     | FALSE | FALSE | null    |
| Neck Breaker 02                            | E     | FALSE | FALSE | null    |
| Piledriver 01                              | D     | FALSE | FALSE | null    |
| Piledriver 02                              | E     | FALSE | FALSE | null    |
| Piledriver 03                              | D     | FALSE | FALSE | null    |
| Piledriver 04                              | D     | FALSE | FALSE | null    |
| Rib Breaker                                | E     | FALSE | FALSE | null    |
| Russian Leg Sweep                          | E     | FALSE | FALSE | null    |
| Shoulder Breaker                           | E     | FALSE | FALSE | null    |
| Shoulder Thrusts                           | E     | FALSE | FALSE | null    |
| Snap Suplex                                | E     | FALSE | FALSE | null    |
| Stall Suplex                               | E     | FALSE | FALSE | null    |
| Suplex                                     | E     | FALSE | FALSE | null    |
| Tie Up Knee Strikes                        | F     | FALSE | FALSE | null    |
| Underhook Suplex / Knee                    | D     | FALSE | FALSE | null    |

## Related

- `data/moves/move-slots.md` — Authoritative slot definitions and input mappings
- `data/moves/move-database.json` — Programmatic version of this file (in progress)
- `data/README.md` — Power tier scale, feature values, and boolean flag definitions
- `assets/characters/{character}/moves.json` — Per-character move assignments
