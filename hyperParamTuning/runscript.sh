THEANO_FLAGS=mode=FAST_RUN,device=gpu0,floatX=float32 nohup python /home/jie/d3/fujie/copy1/hyper_parameter_tuning/hyperParamTuning/HyperParamTuning.py --driver=local --method=RandomChooser --method-args=noiseless=0 --polling-time=20 --max-concurrent=1 -w --port=50000 --max-finished-jobs=10 --mode=generate /home/jie/d3/fujie/copy1/hyper_parameter_tuning/hyperParamTuning/experiment/1/11/example/spear_config.pb &
nohup python /home/jie/d3/fujie/hyper_parameter_tuning/hyperParamServer/serverSpearmintAD.py &