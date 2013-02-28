function runSimulator(filepath, noGUI)
  %% Execute the external binary file of the simulator
  disp('Trajectory exported to input.txt file. Next, the simulator will be executed.');

  settings = getSettings();
  simulator_dir = settings.simulationDir;
  simulator_filename = settings.simulationExecutable;

  if isunix
    command = [simulator_dir, simulator_filename, ' ', filepath, 'output.txt'];
    disp(sprintf('Running command: %s', command));
    [status, out] = system(command);
    if status ~= 0
      warning(sprintf('Exit code was %d', status));
    end
  else
    exe_file = [simulator_dir simulator_filename];
    filepathDOS = strrep(filepath, '/', '\');
    disp('Going to execute command:');
    command1 = ['cd ' simulator_dir]
    command2 = [exe_file ' -i ' filepathDOS 'input.txt' ' -o ' filepathDOS 'output.txt']
    if noGUI == 1
      command2 = [command2 ' -n '];
    end
    if noGUI == 0
      disp('Press ENTER to execute simulator...');
      % pause
    end
    [s,w] = dos([command1 ' & ' command2]);  % TODO: why it's so slow to copy from my VM ubuntu, and so fast from WAM??
  end
%     disp('Press ENTER to continue...');
%     pause
end

