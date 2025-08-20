# Security Configuration

## User Authentication

The Coffee PID Controller uses environment variables for secure credential management.

### Setting Up Credentials

Set the following environment variables before running the application:

```bash
# Admin user credentials
export COFFEE_ADMIN_USER=admin
export COFFEE_ADMIN_PASS=your_secure_admin_password

# Regular user credentials  
export COFFEE_USER_NAME=user
export COFFEE_USER_PASS=your_secure_user_password
```

### Security Best Practices

1. **Use strong passwords**: Choose complex passwords with mixed case, numbers, and special characters
2. **Environment-specific credentials**: Use different credentials for development, testing, and production
3. **Secure storage**: Store credentials in a secure password manager or secrets management system
4. **Regular rotation**: Change passwords periodically
5. **Access control**: Limit access to environment variables to authorized personnel only

### Development Mode

If no environment variables are set, the application will fall back to default credentials with a warning message. This should only be used for development and testing.

### Production Deployment

For production deployment:
- Always set environment variables
- Use a secrets management service
- Consider implementing additional security measures like rate limiting and session management
- Regularly audit access logs