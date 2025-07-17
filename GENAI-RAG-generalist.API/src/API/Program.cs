using Application.Services;
using Domain.Interfaces;
using Infrastructure.Repositories;
using Microsoft.OpenApi.Models;
using Infrastructure.Data;
using Infrastructure.Cache;
using StackExchange.Redis;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "DDD Template API", Version = "v1" });

    // Include XML comments from all projects
    var xmlFiles = new[]
    {
        $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml",
        "Application.xml",
        "Domain.xml",
        "Infrastructure.xml"
    };

    foreach (var xmlFile in xmlFiles)
    {
        var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
        if (File.Exists(xmlPath))
        {
            c.IncludeXmlComments(xmlPath);
        }
    }
});

// Configure Entity Framework
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Configure Redis
builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>
    ConnectionMultiplexer.Connect(builder.Configuration.GetConnectionString("Redis")!));
builder.Services.AddScoped<RedisCacheService>();

// Register dependencies
builder.Services.AddScoped<IProductRepository, ProductRepository>();
builder.Services.AddScoped<ProductService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();
