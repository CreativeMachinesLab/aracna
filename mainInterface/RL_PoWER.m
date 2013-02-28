function [Return, s_Return, param, rl] = RL_PoWER(fromKnots, toKnots, relearn, Return, s_Return, param, rl);
%% RL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
disp('Starting RL...');
%  rl_m = m; % make a copy of m

hFig = figure('Name', 'Rollouts', 'position', [50, 100, 800, 600]);
hFigResults = figure('Name', 'Results', 'position',[1000,600,800,400]); axis on; grid on; hold on;
hFigExported = figure('Name', 'Exported trajectory', 'position', [850, 100, 600, 400]); hold on; box on; grid on;

plotRollouts(hFig, 0, 0, 0, 0);

settings = getSettings();

% START of PoWER algorithm
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% number of iterations
n_iter = 60;
% number of parameters of the policy = number of spline knots here
n_splines = 8;
n_rfs = n_splines*(fromKnots - 1);  % because the last knot of the spline y(n) = y(1)

importanceSamplingTopCount = 3;  % how many top rollouts to use for importance sampling

if relearn==0
  Return = zeros(1,n_iter+1);
  s_Return = zeros(n_iter+1,2);

  % initialize parameters
  param = zeros(n_rfs,n_iter+1);
end

% randn('state',20); % fixed random seed

% set fixed variance
variance(1:n_rfs) = 0.008.*ones(n_rfs,1);
disp('Variance for a single nbState is:');
% variance'
varianceDecay = 0.98;
varianceLog = []; % just to declare the variable

initialPos(0+1) = 600; % joint 0
initialPos(1+1) = 20;
initialPos(2+1) = 600;
initialPos(3+1) = 20;
initialPos(4+1) = 600;
initialPos(5+1) = 20;
initialPos(6+1) = 600;
initialPos(7+1) = 20; % joint 7
%initialPos(8+1) = 512; % body joint - 8
initialPos = initialPos ./ 1024; % normalize in (0,1)

% initial splines
for si=1:n_splines
  policy(1).n_splines = n_splines;
  policy(1).s(si).n = fromKnots; % number of spline knots
  policy(1).s(si).x = 0:1/(policy(1).s(si).n-1):1; % x positions of knots
  policy(1).s(si).y = initialPos(si)*ones(1,policy(1).s(si).n); % set initial policy y values to the middle 0.5
  % now turn it into a cyclic spline
  [policy(1).s(si).pp, policy(1).s(si).x, policy(1).s(si).y, policy(1).s(si).n] = getCyclicSplinePlus6e(policy(1).s(si).x, policy(1).s(si).y);
  plotSpline(policy(1).s(si).pp, policy(1).s(si).n, policy(1).s(si).x, policy(1).s(si).y, 'green', 3); % visualize the spline
end
%pause

% initialize the parameters to optimize with their current values
param(:,1) = policyToParam(policy(1));

disp('param - in the BEGINNING');
param(:,1)'

% pause

disp('Running PoWER algorithm...');

if relearn==1 % resume learning of a previous session
    % load iteration number
    iter_matrix = dlmread([getDataPath() 'iter.txt']);
    iter = iter_matrix(1,1);
    load([getDataPath() num2str(iter,'%03d') '/workspace.mat']); % loads ALL workspace variables!!
    % iter = iter + 1; ?? no, let it repeat it, if necessary I can just reuse the previous reward
    % here make changes to parameters, if necessary, e.g. variability, etc.
    % ...
else
    iter = 1;
end
% do the iterations
while (iter <= n_iter)

    %if (mod(iter,100)==0)
        disp(['Iteration: ', num2str(iter)]);
    %end

%     disp('param:');
%     param(:,iter)'

    if fromKnots < toKnots
        % regularly increase the number of knots
        increaseInterval = round(n_iter / (toKnots - fromKnots));
        if (mod(iter,increaseInterval)==0)
            n_rfs = n_rfs + 1;
            n2 = policy(iter).s(1).n + 1; % TODO: loop for all splines!!!!
            disp(['Increasing the # of knots to ', num2str(n2)]);
            param = zeros(n_rfs,n_iter+1);
            variance(1:n_rfs) = 1.0 * variance(1:1) * ones(n_rfs,1); % copy prev. variance
            for i=1:iter
                [policy(i).s(1).pp, policy(i).s(1).x, policy(i).s(1).y] = getNewSplineCyclic(policy(i).s(1).pp, policy(i).s(1).x, n2);
                policy(i).s(1).n = n2;
                param(:,i) = policy(i).s(1).y(1+3:end-1-3)';
            end
        end
    end

    % plot the rollout / all rollouts so far
    plotRollouts(hFig, iter, iter, policy, n_splines);
    filepath = [getDataPath() num2str(iter,'%03d') '/'];
    mkdir(filepath);
    exportTrajectoryWithoutRescaling(policy(iter), hFigExported, filepath);

    if iter == 1
      noGUI = 0 % 1 to hide the GUI for the first half of trials
    elseif iter < 0.8*n_iter
      noGUI = 0 % 1 to hide the GUI for the first half of trials
    else
      noGUI = 0 % 0 to show the GUI for the second half of trials
    end

    if settings.useRobot
      runRobot();  % TODO: add any robot options here
    else
      runSimulator(filepath, noGUI); % 1 for noGUI
    end

    % for real robot experiment
    rl(iter).traj = Load_trajectory([getDataPath() num2str(iter,'%03d') '/output.txt']);

    % calculate the return of the current rollout
 	  Return(iter) = ReturnOfRollout(rl(iter).traj);
 	  disp(['Current rollout return: ', num2str(Return(iter))]);
     
    % plot the results / all results so far
    plotResults(hFigResults, iter, variance, varianceLog(:,1:iter-1), Return(:,1:iter));
    
    % save iteration number
    dlmwrite([getDataPath() 'iter.txt'], iter);
    %mkdir([getDataPath() num2str(iter,'%03d')]);
    save([getDataPath() num2str(iter,'%03d') '/workspace.mat']); % saves ALL workspace variables!! Nice!
    % disp('Saved workspace. ENTER to continue...');
    % pause
    
    % this lookup table will be used for the importance sampling
    s_Return(1,:) = [Return(iter) iter];
    s_Return = sortrows(s_Return);
    
    % update the policy parameters
    param_nom = zeros(n_rfs,1);
    param_dnom = 0;
    
    if relearn==0
      min_count = iter; % only the rollouts from current batch so far
    else
      min_count = n_iter; % all previous experiences
    end
    % calculate the expectations (the normalization is taken care of by the division)
    % as importance sampling we take the top best rollouts
    for i=1:min(min_count,importanceSamplingTopCount) % TODO: how many are optimal??
      % get the rollout number for the top best rollouts
      j = s_Return(end+1-i,2);

      % calculate the exploration with respect to the current parameters
      temp_explore = (param(:,j)-param(:,iter));

      % always have the same exploration variance, and assume that always only one basis functions is active we get these simple sums
      param_nom = param_nom + temp_explore*(Return(j).^6); % TODO: ^6 to put more weight on the higher rewards
      param_dnom = param_dnom + (Return(j).^6);
    end
    
    % update the parameters
    param(:,iter+1) = param(:,iter) + param_nom./(param_dnom+1.e-10);
    
    % decay the variance
    variance(:) = variance(:) .* varianceDecay;
    varianceLog(1,iter) = variance(1); % TODO: fix size and uncomment line

    % add noise
    param(:,iter+1) = param(:,iter+1) + variance(:).^.5.*randn(n_rfs,1);
       
    % apply the new parameters from RL
    policy(iter+1) = policy(iter); % copy all fields from old policy
    policy(iter+1) = paramToPolicy(param(:, iter+1), policy(iter+1));

iter = iter + 1;    
end % iter loop

iter = iter - 1;

[best_reward best_iter] = max(Return)

disp('param - before the start:');
param(:,1)'

disp('param - best after the RL optimization:');
param(:,best_iter)'

disp('Initial return, before optimization with RL');
Return(1)

disp('Best return:');
Return(best_iter)

% plot the rollout / all rollouts so far
plotResults(hFigResults, iter, variance, varianceLog(:,1:iter-1), Return(:,1:iter));
% plot best traj in red
plotRollouts(hFig, iter, best_iter, policy, n_splines);

% run the best trial again using the simulator  
disp('Press ENTER to see the best trial...');
pause
filepath = [getDataPath() num2str(best_iter,'%03d') '/'];
runSimulator(filepath, 0);

% END of PoWER algorithm
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
end
