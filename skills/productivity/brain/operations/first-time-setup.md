# First-time Setup

1. **Choose a root.** Ask where Brain should live, suggest `~/Brain`, and create or verify the chosen directory.
   - **Complete when:** the user has chosen a directory that exists.
2. **Store configuration.** Write the absolute path to `~/.config/brain/config.json`:

   ```json
   {
     "brain_root": "/absolute/path/to/Brain"
   }
   ```

   - **Complete when:** rereading the file yields the chosen absolute `brain_root` and the directory exists.
