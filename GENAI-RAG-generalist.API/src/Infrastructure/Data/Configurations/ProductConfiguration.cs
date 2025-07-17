using Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Infrastructure.Data.Configurations
{
    public class ProductConfiguration : IEntityTypeConfiguration<Product>
    {
        public void Configure(EntityTypeBuilder<Product> builder)
        {
            builder.HasKey(e => e.Id);

            builder.Property(e => e.Name)
                .IsRequired()
                .HasMaxLength(255);

            builder.Property(e => e.Description)
                .IsRequired()
                .HasMaxLength(1000);

            builder.Property(e => e.URL_Logo)
                .IsRequired()
                .HasMaxLength(500);

            builder.Property(e => e.api_key)
                .IsRequired()
                .HasMaxLength(255);

            builder.Property(e => e.assistant_id)
                .IsRequired()
                .HasMaxLength(255);

            builder.Property(e => e.realm_id)
                .IsRequired()
                .HasMaxLength(255);

            builder.Property(e => e.CreatedAt)
                .IsRequired()
                .HasDefaultValueSql("CURRENT_TIMESTAMP");

            builder.Property(e => e.UpdatedAt)
                .IsRequired(false);
        }
    }
}