using System.Net;
using System.Net.Http.Json;
using Controller.UnitTests.Base;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Logging;
using Moq;

namespace Controller.UnitTests;

public class WeatherForecastControllerTests : ControllerTestBase
{
    private readonly Mock<ILogger<WeatherForecastController>> _loggerMock;
    private readonly string _baseUrl = "/weatherforecast";

    public WeatherForecastControllerTests()
    {
        _loggerMock = MockRepository.Create<ILogger<WeatherForecastController>>();
    }

    [Fact]
    public async Task Get_ShouldReturnOkWithWeatherForecasts()
    {
        // Act
        var response = await Client.GetAsync(_baseUrl);

        // Assert
        response.Should().BeSuccessful();
        var result = await response.Content.ReadFromJsonAsync<List<WeatherForecast>>();
        result.Should().NotBeNull();
        result.Should().HaveCount(5);
        result.Should().AllSatisfy(forecast =>
        {
            forecast.Date.Should().NotBeNull();
            forecast.TemperatureC.Should().BeInRange(-20, 55);
            forecast.Summary.Should().NotBeNullOrEmpty();
        });
    }

    [Fact]
    public async Task Get_ShouldReturnValidJson()
    {
        // Act
        var response = await Client.GetAsync(_baseUrl);

        // Assert
        response.Should().BeSuccessful();
        response.Content.Headers.ContentType.Should().NotBeNull();
        response.Content.Headers.ContentType!.ToString().Should().Contain("application/json");
    }
}