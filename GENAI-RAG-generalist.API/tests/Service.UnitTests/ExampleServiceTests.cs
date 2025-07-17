using FluentAssertions;
using Moq;
using Service.UnitTests.Base;

namespace Service.UnitTests;

public class ExampleServiceTests : ServiceTestBase
{
    private readonly Mock<IExampleRepository> _repositoryMock;
    private readonly IExampleService _service;

    public ExampleServiceTests()
    {
        _repositoryMock = MockRepository.Create<IExampleRepository>();
        _service = new ExampleService(_repositoryMock.Object);
    }

    [Fact]
    public async Task GetById_WhenEntityExists_ShouldReturnEntity()
    {
        // Arrange
        var id = Guid.NewGuid();
        var expectedEntity = new ExampleEntity { Id = id, Name = "Test" };
        _repositoryMock.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync(expectedEntity);

        // Act
        var result = await _service.GetByIdAsync(id);

        // Assert
        result.Should().NotBeNull();
        result.Should().BeEquivalentTo(expectedEntity);
        VerifyAll();
    }

    [Fact]
    public async Task GetById_WhenEntityDoesNotExist_ShouldReturnNull()
    {
        // Arrange
        var id = Guid.NewGuid();
        _repositoryMock.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync((ExampleEntity)null);

        // Act
        var result = await _service.GetByIdAsync(id);

        // Assert
        result.Should().BeNull();
        VerifyAll();
    }

    [Fact]
    public async Task Create_WithValidData_ShouldCreateEntity()
    {
        // Arrange
        var entity = new ExampleEntity { Name = "Test" };
        _repositoryMock.Setup(x => x.CreateAsync(entity))
            .ReturnsAsync(entity);

        // Act
        var result = await _service.CreateAsync(entity);

        // Assert
        result.Should().NotBeNull();
        result.Should().BeEquivalentTo(entity);
        VerifyAll();
    }
}