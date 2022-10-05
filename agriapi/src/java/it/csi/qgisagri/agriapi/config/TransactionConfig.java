package it.csi.qgisagri.agriapi.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import org.springframework.transaction.jta.JtaTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

@Configuration
@EnableTransactionManagement
public class TransactionConfig
{

  @Bean
  public JtaTransactionManager transactionManager()
  {
    JtaTransactionManager jtaTransactionManager = new JtaTransactionManager();
    return jtaTransactionManager;
  }

  @Bean
  public TransactionTemplate transactionTemplate()
  {
    TransactionTemplate transactionTemplate = new TransactionTemplate();
    transactionTemplate.setTransactionManager(transactionManager());
    return transactionTemplate;
  }
}