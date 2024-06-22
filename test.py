from flappy_bird_env import FlappyBirdEnv
import pygame

render = True

env = FlappyBirdEnv(render) 

env.reset()

clock = pygame.time.Clock()


input_list = [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
input_index = 0

while True:

    if render:
        clock.tick(15)

    action = input_list[input_index]
    input_index = (input_index + 1) % len(input_list)

    state, reward, terminated, truncated, info = env.step(action)

    print(state)
    print(reward)
    
    if terminated:
        print(env.score)
        env.reset()
        input_index = 0