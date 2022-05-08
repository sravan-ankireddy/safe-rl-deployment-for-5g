import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import yaml
import os
from trainers.global_trainer import GlobalTrainer
from env.dynamic_envinronment import Environment
from global_config import ROOT_DIR, DATA_STORAGE
from tf2rl.algos.sac_discrete import SACDiscrete
from trainers.conditional_trainer import ConditionalTrainer
from env.dynamic_envinronment import Environment

def train_agent_with_env(config):
    env = Environment(config=config, TRAIN_MODE=False)
    trainer = GlobalTrainer(config=config, env=env, policy=None)
    trainer()


if __name__ == '__main__':
    # get configuration
    with open(os.path.join(ROOT_DIR,"config.yaml"), "r") as stream:
        try:
            config = yaml.safe_load(stream)
            # print(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

    # Generate / Load Dataset
    if config["generate_dataset"] is True:
        from env.data_generators.scenario_02 import Scenario
        my_scene = Scenario(config)
        my_scene.generate_data()


    env = Environment(config=config, TRAIN_MODE=True)
    test_env = Environment(config=config, TRAIN_MODE=False)



    for num_trial in range(config["algorithm_config"]["trial"]):
        print("==================================================")
        print("==================================================")
        print("==================================================")
        print("=============trial "+str(num_trial) +"=================")
        print("==================================================")
        print("==================================================")

        # Agent Setting
        # Codes are copied from Kei-Ota's project
        parser = ConditionalTrainer.get_argument()
        parser = SACDiscrete.get_argument(parser)
        parser.set_defaults(test_interval=100)
        parser.set_defaults(max_steps=20000)
        parser.set_defaults(gpu=1)
        parser.set_defaults(n_warmup=0)
        parser.set_defaults(batch_size=32)
        parser.set_defaults(memory_capacity=int(1e4))
        parser.add_argument('--env-name', type=str,
                            default="SpaceInvadersNoFrameskip-v4")
        args = parser.parse_args()

        # env = gym.make(args.env_name)
        # test_env = gym.make(args.env_name)

        policy = SACDiscrete(
            state_shape=env.observation_space.shape,
            action_dim=env.action_space.n,
            actor_units=(256, 128),
            discount=0.995,
            lr=0.0001,
            memory_capacity=args.memory_capacity,
            batch_size=args.batch_size,
            n_warmup=args.n_warmup,
            target_update_interval=args.target_update_interval,
            auto_alpha=args.auto_alpha,
            gpu=args.gpu)
        trainer = ConditionalTrainer(policy, env, args, test_env=test_env)
        if args.evaluate:
            trainer.evaluate_policy_continuously()
        else:
            trainer()

