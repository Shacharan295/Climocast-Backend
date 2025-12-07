@echo on
cd /d "D:\Weather AI MODEL"

call venv\Scripts\activate

python training\train_temperature.py
echo Finished temperature model

python training\train_weather.py
echo Finished weather model

python training\train_wind.py
echo Finished wind model

deactivate
echo Done.
pause
