from Subject import WeatherData
from displays import CurrentConditionsDisplay, StatisticsDisplay, ForecastDisplay


def main():
    print("=== Demo Observer PULL ===")

    weather_data = WeatherData()

    current = CurrentConditionsDisplay(weather_data)
    stats = StatisticsDisplay(weather_data)
    forecast = ForecastDisplay(weather_data)

    print("\n-- Actualización #1 --")
    weather_data.set_measurements(26.3, 65, 1013.1)

    print("\n-- Actualización #2 --")
    weather_data.set_measurements(27.8, 70, 1012.4)

    print("\n(Remuevo StatisticsDisplay)")
    weather_data.remove_observer(stats)

    print("\n-- Actualización #3 --")
    weather_data.set_measurements(25.5, 90, 1009.8)

    print("\n(Vuelvo a agregar StatisticsDisplay)")
    stats = StatisticsDisplay(weather_data)

    print("\n-- Actualización #4 --")
    weather_data.set_measurements(23.7, 85, 1011.0)

    print("\n=== Fin de la demo PULL ===")

if __name__ == "__main__":
    main()



