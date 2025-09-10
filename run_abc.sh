# Get the absolute path to your environment
ENV_PATH="$(pwd)/env/bin/activate"

gnome-terminal  -- bash -c "source '$ENV_PATH' && python main_c.py; exec bash"
gnome-terminal  -- bash -c "source '$ENV_PATH' && python main_a.py; exec bash"
gnome-terminal  -- bash -c "source '$ENV_PATH' && python main_b.py; exec bash"


