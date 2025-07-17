using FluentAssertions;
using Moq;

namespace Service.UnitTests.Base;

public abstract class ServiceTestBase
{
    protected readonly MockRepository MockRepository;

    protected ServiceTestBase()
    {
        MockRepository = new MockRepository(MockBehavior.Strict);
    }

    protected virtual void Setup()
    {
        // Common setup code for all service tests
    }

    protected virtual void TearDown()
    {
        // Common cleanup code for all service tests
    }

    protected void VerifyAll()
    {
        MockRepository.VerifyAll();
    }

    protected void VerifyNoOtherCalls()
    {
        MockRepository.VerifyNoOtherCalls();
    }
}