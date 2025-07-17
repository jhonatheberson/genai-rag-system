using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Moq;

namespace Controller.UnitTests.Base;

public abstract class ControllerTestBase : IAsyncLifetime
{
    protected readonly WebApplicationFactory<Program> Application;
    protected readonly HttpClient Client;
    protected readonly IServiceScope Scope;
    protected readonly MockRepository MockRepository;

    protected ControllerTestBase()
    {
        Application = new WebApplicationFactory<Program>();
        Client = Application.CreateClient();
        Scope = Application.Services.CreateScope();
        MockRepository = new MockRepository(MockBehavior.Strict);
    }

    public virtual async Task InitializeAsync()
    {
        // Common setup code for all controller tests
    }

    public virtual async Task DisposeAsync()
    {
        Scope.Dispose();
        Client.Dispose();
        await Application.DisposeAsync();
    }

    protected void VerifyAll()
    {
        MockRepository.VerifyAll();
    }

    protected void VerifyNoOtherCalls()
    {
        MockRepository.VerifyNoOtherCalls();
    }

    protected T GetService<T>() where T : class
    {
        return Scope.ServiceProvider.GetRequiredService<T>();
    }
}