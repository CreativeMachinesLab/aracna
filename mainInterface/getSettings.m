function settings = getSettings()
  % just loads localSettings.m

  try
    settings = localSettings();
  catch
    error('Could not load localSettings.m. Did you create it from localSettings.m.template?');
  end
end

