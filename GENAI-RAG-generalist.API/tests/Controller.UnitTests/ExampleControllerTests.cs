using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Moq;
using Controller.UnitTests.Base;

namespace Controller.UnitTests;

public class ExampleControllerTests : ControllerTestBase
{
    private readonly Mock<IExampleService> _serviceMock;

    public ExampleControllerTests()
    {
        _serviceMock = MockRepository.Create<IExampleService>();
    }

    [Fact]
    public async Task GetById_WhenEntityExists_ShouldReturnOkWithEntity()
    {
        // Arrange
        var id = Guid.NewGuid();
        var expectedEntity = new ExampleEntity { Id = id, Name = "Test" };
        _serviceMock.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync(expectedEntity);

        // Act
        var response = await Client.GetAsync($"/api/example/{id}");

        // Assert
        response.Should().BeSuccessful();
        var result = await response.Content.ReadFromJsonAsync<ExampleEntity>();
        result.Should().BeEquivalentTo(expectedEntity);
        VerifyAll();
    }

    [Fact]
    public async Task GetById_WhenEntityDoesNotExist_ShouldReturnNotFound()
    {
        // Arrange
        var id = Guid.NewGuid();
        _serviceMock.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync((ExampleEntity)null);

        // Act
        var response = await Client.GetAsync($"/api/example/{id}");

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.NotFound);
        VerifyAll();
    }

    [Fact]
    public async Task Create_WithValidData_ShouldReturnCreated()
    {
        // Arrange
        var entity = new ExampleEntity { Name = "Test" };
        _serviceMock.Setup(x => x.CreateAsync(entity))
            .ReturnsAsync(entity);

        // Act
        var response = await Client.PostAsJsonAsync("/api/example", entity);

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.Created);
        var result = await response.Content.ReadFromJsonAsync<ExampleEntity>();
        result.Should().BeEquivalentTo(entity);
        VerifyAll();
    }

    [Fact]
    public async Task Create_WithInvalidData_ShouldReturnBadRequest()
    {
        // Arrange
        var entity = new ExampleEntity { Name = "" }; // Invalid data

        // Act
        var response = await Client.PostAsJsonAsync("/api/example", entity);

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.BadRequest);
        VerifyNoOtherCalls();
    }
}