# Ian_Betto_OOP
![Tests](https://github.com/Audichin/Ian_Bero_OOP/actions/workflows/ci-test.yml/badge.svg)


Ian and Heriberto OOP project

| Name                | Value                                          |
| :------------------ | :--------------------------------------------- |
| **Course**          | CSCI375 - OOP and Design Patterns              |
| **Section**         | 1                                              |
| **Semester**        | Spring 20256                                   |
| **Students**        | Ian Mooney & Heriberto Dominguez                |
| **Mav Usernames**   | Imooney & bdominguez                           |
| **GitHub Username** | Audichin                                       |
| **Repository**      | https://github.com/Audichin/Ian_Bero_OOP.git   |

## Assignments

### Project

| Name        | Value                                                                                                                            |
| :---------- | :------------------------------------------------------------------------------------------------------------------------------- |
| Name        |                                                                                                                                  |
| Description |                                                                                                                                  |
| Due Date    | --/--/----                                                                                                                       |
| Status      |                                                                                                                                  |
| Location    |                                                                                                                                  |
|Code Location|                                                                                                                                  |
| Self Grade  | ---/---                                                                                                                          |
| Notes       |                                                                                                                                  |

# Difficulties with Docker
> [!NOTE]
> Docker doesn't support GUI or sound out the box.

On UNIX machines it is simple to link hardware sound devices to a docker container. This functionality, however, is **NOT** present on windows machines. When running any python module with pygame imported and utilized, the following errors are displayed in the docker console:
```
pygame 2.6.1 (SDL 2.28.4, Python 3.12.12)
Hello from the pygame community. https://www.pygame.org/contribute.html
ALSA lib confmisc.c:855:(parse_card) cannot find card '0'
ALSA lib conf.c:5205:(_snd_config_evaluate) function snd_func_card_inum returned error: No such file or directory
ALSA lib confmisc.c:422:(snd_func_concat) error evaluating strings
ALSA lib conf.c:5205:(_snd_config_evaluate) function snd_func_concat returned error: No such file or directory
ALSA lib confmisc.c:1342:(snd_func_refer) error evaluating name
ALSA lib conf.c:5205:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
ALSA lib conf.c:5728:(snd_config_expand) Evaluate error: No such file or directory
ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM default
```
These errors are a result of ALSA being unable to find sound hardware in the confines of the docker. Allowing sound capabilities on windows machines would require the user to install third-party software (pulse-audio) and make changes to do the software configs.

> [!NOTE] 
> If you have Xming installed on your windows machine, running the game in the docker should work. The display provided is created by xhost. Ensure before running the program that Xming is running.

For unit-testing, program-testing, github actions, and ensuring the project adheres to pep8 best practices, utilize the docker. For play-testing, run the game natively on your machine.

### <ins>If you intend to play the game, it is recommended you run the program natively on your machine with pygame version 2.6.1 installed.</ins>