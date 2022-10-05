package it.csi.qgisagri.agriapi.config;

import javax.sql.DataSource;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jndi.JndiObjectFactoryBean;

import it.csi.qgisagri.agriapi.util.AgriApiConstants;

/**
 * Depending active spring profile, lookup RDBMS DataSource from JNDI or from an
 * embbeded H2 database.
 */
@Configuration
public class DataSourceConfig
{
  @Bean
  public JndiObjectFactoryBean dataSource() throws IllegalArgumentException
  {
    JndiObjectFactoryBean dataSource = new JndiObjectFactoryBean();
    dataSource.setExpectedType(DataSource.class);
    dataSource.setJndiName(AgriApiConstants.DATABASE.JNDINAME);
    return dataSource;
  }
}